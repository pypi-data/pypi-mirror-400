# Solar engine - v1.0.4 (solar packages: contain solar.<pkg> + pkg.func calls)
# Exports: SOLAR_VERSION, compile_to_python, run_file
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SOLAR_VERSION = "1.0.4"


# ---------------- AST ----------------
@dataclass
class Stmt: ...
@dataclass
class Expr: ...

@dataclass
class Number(Expr):
    value: float

@dataclass
class String(Expr):
    value: str

@dataclass
class Var(Expr):
    name: str

@dataclass
class Let(Stmt):
    name: str
    expr: Expr

@dataclass
class Print(Stmt):
    exprs: list[Expr]

@dataclass
class Call(Stmt):
    name: str
    args: list[Expr]

@dataclass
class SolarDef(Stmt):
    name: str
    args: list[str]          # may be empty
    body: list[Stmt]

@dataclass
class Contain(Stmt):
    module: str

@dataclass
class UiStmt(Stmt):
    cmd: str
    args: list[str]
    quoted: list[bool]


# ---------------- Tokenizer (keeps whether token was quoted) ----------------
def _tokenize_with_quotes(line: str) -> list[tuple[str, bool]]:
    out: list[tuple[str, bool]] = []
    i = 0
    n = len(line)

    while i < n:
        while i < n and line[i].isspace():
            i += 1
        if i >= n:
            break

        ch = line[i]
        if ch in ('"', "'"):
            q = ch
            i += 1
            buf: list[str] = []
            while i < n:
                if line[i] == "\\" and i + 1 < n:
                    buf.append(line[i + 1])
                    i += 2
                    continue
                if line[i] == q:
                    break
                buf.append(line[i])
                i += 1
            if i >= n or line[i] != q:
                raise SyntaxError("Oh noes! Solar threw an error: unclosed string literal")
            i += 1
            out.append(("".join(buf), True))
        else:
            j = i
            while j < n and not line[j].isspace():
                j += 1
            out.append((line[i:j], False))
            i = j

    return out


def _parse_expr(tok: str, was_quoted: bool) -> Expr:
    if was_quoted:
        return String(tok)
    try:
        if "." in tok:
            return Number(float(tok))
        return Number(int(tok))
    except ValueError:
        # NOTE: this returns Var even for tokens like "pkg.func"
        # That's fine because pkg calls are parsed as CALL HEAD, not expression.
        return Var(tok)


def _parse_simple_stmt(line: str, lineno: int) -> Stmt:
    parts_q = _tokenize_with_quotes(line)
    if not parts_q:
        raise SyntaxError("empty")
    parts = [t for t, _q in parts_q]
    quoted = [q for _t, q in parts_q]

    head = parts[0]

    if head == "contain":
        if len(parts) < 2:
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: `contain <module>` expected")
        mod = parts[1].strip().rstrip(" ;,")
        if "#" in mod:
            mod = mod.split("#", 1)[0].strip()
        # allow solar.<pkgname> (with dash in docs) -> we will accept dash in pkg name here ONLY
        if mod.startswith("solar."):
            pkg = mod[len("solar."):].strip()
            if not pkg:
                raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: invalid solar package name")
            return Contain("solar." + pkg)

        # normal python module import rules
        if not mod or not all(p.isidentifier() for p in mod.split(".")):
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: invalid module name for contain")
        return Contain(mod)

    if head == "let":
        if len(parts) < 4 or parts[2] != "=":
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: expected `let <name> = <expr>`")
        name = parts[1]
        expr = _parse_expr(parts[3], quoted[3])
        return Let(name, expr)

    if head == "print":
        if len(parts) < 2:
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: expected `print <expr...>`")
        return Print([_parse_expr(parts[i], quoted[i]) for i in range(1, len(parts))])

    if head == "ui":
        if len(parts) < 2:
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: bad ui statement")
        return UiStmt(parts[1], parts[2:], quoted[2:])

    return Call(head, [_parse_expr(parts[i], quoted[i]) for i in range(1, len(parts))])


def parse_program(src: str) -> list[Stmt]:
    lines = src.splitlines()
    i = 0
    out: list[Stmt] = []

    while i < len(lines):
        raw = lines[i]
        i += 1
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("solar_def"):
            rest = line[len("solar_def"):].strip()
            if not rest.endswith(":"):
                raise SyntaxError("Oh noes! Solar threw an error: solar_def must end with ':'")
            rest = rest[:-1].strip()

            name = rest
            args: list[str] = []

            if "(" in rest and rest.endswith(")"):
                name, arg_str = rest.split("(", 1)
                arg_str = arg_str[:-1]
                if arg_str.strip():
                    args = [a.strip() for a in arg_str.split(",") if a.strip()]
            elif rest.endswith("()"):
                name = rest[:-2]
                args = []
            else:
                name = rest
                args = []

            if not name.strip().isidentifier():
                raise SyntaxError("Oh noes! Solar threw an error: invalid function name in solar_def")

            body: list[Stmt] = []
            while i < len(lines):
                inner_raw = lines[i]
                i += 1
                inner = inner_raw.strip()
                if not inner or inner.startswith("#"):
                    continue
                if inner == "end":
                    break
                body.append(_parse_simple_stmt(inner, i))
            else:
                raise SyntaxError("Oh noes! Solar threw an error: solar_def missing `end`")

            out.append(SolarDef(name.strip(), args, body))
            continue

        out.append(_parse_simple_stmt(line, i))

    return out


# ---------------- Compilation ----------------
def _emit_expr(e: Expr) -> str:
    if isinstance(e, Number):
        return repr(e.value)
    if isinstance(e, String):
        return repr(e.value)
    if isinstance(e, Var):
        return f"vars_.get({e.name!r})"
    raise TypeError(e)


def compile_to_python(src: str) -> str:
    program = parse_program(src)
    imports: set[str] = set()

    for st in program:
        if isinstance(st, Contain):
            # normal imports only (NOT solar.<pkg>)
            if not st.module.startswith("solar."):
                imports.add(st.module)

    out: list[str] = []
    out.append("# compiled by Solar")
    for m in sorted(imports):
        out.append(f"import {m}")
    out.append("")
    out.append("def __run(vars_, funcs):")
    out.append("    # vars_: variable storage, funcs: function registry")
    out.append("    __solar_fns = {}")
    out.append("")
    out.append("    def __call(name, *args):")
    out.append("        f = funcs.get(name)")
    out.append("        if f is None:")
    out.append("            f = __solar_fns.get(name)")
    out.append("        if f is None:")
    out.append("            raise NameError('Oh noes! Solar threw an error: Unknown function: ' + str(name))")
    out.append("        return f(*args)")
    out.append("")

    # minimal UI backend
    out.append("    __wins = {}")
    out.append("    __widgets = {}")
    out.append("    __uivars = {}")
    out.append("    def __ui(cmd, *args):")
    out.append("        nonlocal __wins, __widgets, __uivars")
    out.append("        if cmd == 'window':")
    out.append("            name = args[0]")
    out.append("            __wins[name] = CTk()")
    out.append("            return")
    out.append("        if cmd == 'title':")
    out.append("            win, title = args[0], args[1]")
    out.append("            __wins[win].title(title)")
    out.append("            return")
    out.append("        if cmd == 'size':")
    out.append("            win, w, h = args[0], args[1], args[2]")
    out.append("            __wins[win].geometry(str(int(float(w))) + 'x' + str(int(float(h))))")
    out.append("            return")
    out.append("        if cmd == 'bg':")
    out.append("            win, color = args[0], args[1]")
    out.append("            try: __wins[win].configure(fg_color=color)")
    out.append("            except Exception:")
    out.append("                try: __wins[win].configure(bg=color)")
    out.append("                except Exception: pass")
    out.append("            return")
    out.append("        if cmd == 'fg':")
    out.append("            win, color = args[0], args[1]")
    out.append("            vars_['__ui_fg_' + win] = color")
    out.append("            return")
    out.append("        if cmd == 'label':")
    out.append("            win, name, text = args[0], args[1], args[2]")
    out.append("            if 'at' in args:")
    out.append("                ai = list(args).index('at')")
    out.append("                x = float(args[ai+1]); y = float(args[ai+2])")
    out.append("            else:")
    out.append("                x = 0; y = 0")
    out.append("            fg = vars_.get('__ui_fg_' + win)")
    out.append("            try: w = CTkLabel(__wins[win], text=text, text_color=fg if fg is not None else None)")
    out.append("            except Exception: w = Label(__wins[win], text=text)")
    out.append("            try: w.place(x=x, y=y)")
    out.append("            except Exception: pass")
    out.append("            __widgets[name] = w")
    out.append("            return")
    out.append("        if cmd == 'entry':")
    out.append("            win, name = args[0], args[1]")
    out.append("            ai = list(args).index('at') if 'at' in args else -1")
    out.append("            x = float(args[ai+1]) if ai!=-1 else 0")
    out.append("            y = float(args[ai+2]) if ai!=-1 else 0")
    out.append("            sv = StringVar()")
    out.append("            try: w = CTkEntry(__wins[win], textvariable=sv)")
    out.append("            except Exception: w = Entry(__wins[win], textvariable=sv)")
    out.append("            try: w.place(x=x, y=y)")
    out.append("            except Exception: pass")
    out.append("            __widgets[name] = w")
    out.append("            __uivars[name] = sv")
    out.append("            vars_[name] = sv")
    out.append("            return")
    out.append("        if cmd == 'checkbox':")
    out.append("            win, name, text = args[0], args[1], args[2]")
    out.append("            ai = list(args).index('at') if 'at' in args else -1")
    out.append("            x = float(args[ai+1]) if ai!=-1 else 0")
    out.append("            y = float(args[ai+2]) if ai!=-1 else 0")
    out.append("            iv = IntVar()")
    out.append("            fg = vars_.get('__ui_fg_' + win)")
    out.append("            try: w = CTkCheckBox(__wins[win], text=text, variable=iv, text_color=fg if fg is not None else None)")
    out.append("            except Exception: w = Checkbutton(__wins[win], text=text, variable=iv)")
    out.append("            try: w.place(x=x, y=y)")
    out.append("            except Exception: pass")
    out.append("            __widgets[name] = w")
    out.append("            __uivars[name] = iv")
    out.append("            vars_[name] = iv")
    out.append("            return")
    out.append("        if cmd == 'button':")
    out.append("            win, name, text = args[0], args[1], args[2]")
    out.append("            ai = list(args).index('at') if 'at' in args else -1")
    out.append("            di = list(args).index('do') if 'do' in args else -1")
    out.append("            x = float(args[ai+1]) if ai!=-1 else 0")
    out.append("            y = float(args[ai+2]) if ai!=-1 else 0")
    out.append("            fn = args[di+1] if di!=-1 and di+1 < len(args) else None")
    out.append("            raw_call_args = list(args[di+2:]) if di!=-1 else []")
    out.append("            def _cb():")
    out.append("                if fn is None: return")
    out.append("                call_args = []")
    out.append("                for a in raw_call_args:")
    out.append("                    call_args.append(vars_.get(a, a))")
    out.append("                return __call(fn, *call_args)")
    out.append("            fg = vars_.get('__ui_fg_' + win)")
    out.append("            try: w = CTkButton(__wins[win], text=text, command=_cb, text_color=fg if fg is not None else None)")
    out.append("            except Exception: w = Button(__wins[win], text=text, command=_cb)")
    out.append("            try: w.place(x=x, y=y)")
    out.append("            except Exception: pass")
    out.append("            __widgets[name] = w")
    out.append("            return")
    out.append("        if cmd == 'text':")
    out.append("            wname, newt = args[0], args[1]")
    out.append("            w = __widgets.get(wname)")
    out.append("            if w is None: raise NameError('Oh noes! Solar threw an error: Unknown widget: ' + str(wname))")
    out.append("            try: w.configure(text=newt)")
    out.append("            except Exception:")
    out.append("                try: w.config(text=newt)")
    out.append("                except Exception: pass")
    out.append("            return")
    out.append("        if cmd == 'run':")
    out.append("            win = args[0]")
    out.append("            __wins[win].mainloop()")
    out.append("            return")
    out.append("        raise NameError('Oh noes! Solar threw an error: Unknown ui command: ' + str(cmd))")
    out.append("")

    def emit_stmt(st: Stmt, indent: str) -> None:
        if isinstance(st, Contain):
            # ignore solar.<pkg> in compiled output (engine loads packages before running)
            return

        if isinstance(st, Let):
            out.append(f"{indent}vars_[{st.name!r}] = {_emit_expr(st.expr)}")
            return

        if isinstance(st, Print):
            out.append(f"{indent}print(" + ", ".join(_emit_expr(e) for e in st.exprs) + ")")
            return

        if isinstance(st, UiStmt):
            arglist = ", ".join(repr(a) for a in st.args)
            out.append(f"{indent}__ui({st.cmd!r}, {arglist})" if arglist else f"{indent}__ui({st.cmd!r})")
            return

        if isinstance(st, SolarDef):
            arglist = ", ".join(st.args)
            out.append(f"{indent}def {st.name}({arglist}):")
            if not st.body:
                out.append(indent + "    pass")
            else:
                for inner in st.body:
                    emit_stmt(inner, indent + "    ")
            out.append(f"{indent}__solar_fns[{st.name!r}] = {st.name}")
            out.append(f"{indent}funcs.setdefault({st.name!r}, {st.name})")
            return

        if isinstance(st, Call):
            args = ", ".join(_emit_expr(a) for a in st.args)
            out.append(f"{indent}__call({st.name!r}" + (f", {args}" if args else "") + ")")
            return

        raise TypeError(st)

    for st in program:
        emit_stmt(st, "    ")

    out.append("")
    return "\n".join(out)


# ---------------- Solar package loader ----------------
def _solar_packages_root() -> Path:
    return Path.home() / ".solar" / "packages"


def _find_main_solar(pkg_dir: Path) -> Path | None:
    for p in pkg_dir.rglob("main.solar"):
        if p.is_file():
            return p
    return None


def _load_solar_package(pkg_name: str, funcs: dict[str, Callable[..., Any]]) -> None:
    """
    Loads ~/.solar/packages/pkg-<name>/main.solar and registers all functions as "<name>.<func>".
    """
    pkg_dir = _solar_packages_root() / f"pkg-{pkg_name}"
    if not pkg_dir.exists():
        raise NameError(f"Oh noes! Solar threw an error: Solar package not installed: {pkg_name}")

    main = _find_main_solar(pkg_dir)
    if main is None:
        raise NameError(f"Oh noes! Solar threw an error: main.solar not found for package: {pkg_name}")

    # run package code in its own vars_ but shared function dict used to collect exports
    pkg_funcs: dict[str, Callable[..., Any]] = {}

    # basic print helpers (so package can print)
    def print_many(*items):
        out_items = []
        for it in items:
            try:
                if hasattr(it, "get") and callable(it.get):
                    out_items.append(it.get())
                else:
                    out_items.append(it)
            except Exception:
                out_items.append(it)
        print(*out_items)

    pkg_funcs["print"] = print_many
    pkg_funcs["print_many"] = print_many

    # compile + exec package
    src = main.read_text(encoding="utf-8")
    py_src = compile_to_python(src)
    tree = ast.parse(py_src, mode="exec")

    # same UI backend as main
    import tkinter as tk
    try:
        import customtkinter as ctk
        CTk = ctk.CTk
        CTkLabel = ctk.CTkLabel
        CTkButton = ctk.CTkButton
        CTkEntry = ctk.CTkEntry
        CTkCheckBox = ctk.CTkCheckBox
    except Exception:
        CTk = tk.Tk
        CTkLabel = tk.Label
        CTkButton = tk.Button
        CTkEntry = tk.Entry
        CTkCheckBox = tk.Checkbutton

    safe_globals: dict[str, Any] = {
        "__builtins__": {
            "__import__": __import__,
            "print": print,
            "NameError": NameError,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "Exception": Exception,
            "str": str,
            "int": int,
            "float": float,
            "len": len,
            "range": range,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "getattr": getattr,
            "hasattr": hasattr,
            "callable": callable,
        },
        "StringVar": tk.StringVar,
        "IntVar": tk.IntVar,
        "Label": tk.Label,
        "Button": tk.Button,
        "Entry": tk.Entry,
        "Checkbutton": tk.Checkbutton,
        "CTk": CTk,
        "CTkLabel": CTkLabel,
        "CTkButton": CTkButton,
        "CTkEntry": CTkEntry,
        "CTkCheckBox": CTkCheckBox,
    }

    local_env: dict[str, Any] = {}
    exec(compile(tree, filename="<solar_pkg>", mode="exec"), safe_globals, local_env)
    pkg_vars: dict[str, Any] = {}
    local_env["__run"](pkg_vars, pkg_funcs)

    # export functions into main funcs as "pkg.func"
    for k, v in list(pkg_funcs.items()):
        if k in ("print", "print_many"):
            continue
        if callable(v):
            funcs[f"{pkg_name}.{k}"] = v


# ---------------- Execution ----------------
def run_file(path: str | Path, funcs: dict[str, Callable[..., Any]] | None = None) -> None:
    p = Path(path)
    src = p.read_text(encoding="utf-8")

    # Parse once to discover solar.<pkg> contains
    program = parse_program(src)
    solar_pkgs: set[str] = set()
    for st in program:
        if isinstance(st, Contain) and st.module.startswith("solar."):
            pkg = st.module[len("solar."):].strip()
            # accept dash names in contain solar.<pkg-name>
            pkg = pkg.replace("-", "_") if False else pkg  # keep as-is; you can choose policy
            solar_pkgs.add(pkg)

    py_src = compile_to_python(src)
    tree = ast.parse(py_src, mode="exec")

    import tkinter as tk
    try:
        import customtkinter as ctk
        CTk = ctk.CTk
        CTkLabel = ctk.CTkLabel
        CTkButton = ctk.CTkButton
        CTkEntry = ctk.CTkEntry
        CTkCheckBox = ctk.CTkCheckBox
    except Exception:
        CTk = tk.Tk
        CTkLabel = tk.Label
        CTkButton = tk.Button
        CTkEntry = tk.Entry
        CTkCheckBox = tk.Checkbutton

    safe_globals: dict[str, Any] = {
        "__builtins__": {
            "__import__": __import__,
            "print": print,
            "NameError": NameError,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "Exception": Exception,
            "str": str,
            "int": int,
            "float": float,
            "len": len,
            "range": range,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "getattr": getattr,
            "hasattr": hasattr,
            "callable": callable,
        },
        "StringVar": tk.StringVar,
        "IntVar": tk.IntVar,
        "Label": tk.Label,
        "Button": tk.Button,
        "Entry": tk.Entry,
        "Checkbutton": tk.Checkbutton,
        "CTk": CTk,
        "CTkLabel": CTkLabel,
        "CTkButton": CTkButton,
        "CTkEntry": CTkEntry,
        "CTkCheckBox": CTkCheckBox,
    }

    local_env: dict[str, Any] = {}
    exec(compile(tree, filename="<solar>", mode="exec"), safe_globals, local_env)

    vars_: dict[str, Any] = {}

    if funcs is None:
        funcs = {}

        def print_many(*items):
            out_items = []
            for it in items:
                try:
                    if hasattr(it, "get") and callable(it.get):
                        out_items.append(it.get())
                    else:
                        out_items.append(it)
                except Exception:
                    out_items.append(it)
            print(*out_items)

        funcs["print"] = print_many
        funcs["print_many"] = print_many

    # Load solar packages before running main
    for pkg in sorted(solar_pkgs):
        _load_solar_package(pkg, funcs)

    local_env["__run"](vars_, funcs)
