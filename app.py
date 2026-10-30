import streamlit as st
import math
import cmath
import ast
import operator

# ==============================
# IZHAM SCIENTIFIC CALCULATOR
# Watermark: made of izham
# ==============================

st.set_page_config(
    page_title="Izham Scientific Calculator",
    page_icon="🧮",
    layout="centered"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(145deg, #080d1c, #111b35, #17102b);
    color: white;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
}

h1 {
    color: #ffffff;
    text-align: center;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    color: #a9b8d6;
    margin-bottom: 25px;
}

.brand {
    text-align: center;
    color: #8b9cff;
    font-size: 13px;
    letter-spacing: 3px;
    font-weight: bold;
    margin-top: 30px;
}

.result {
    background: linear-gradient(100deg, #172d56, #34245d);
    border: 1px solid #657cff;
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
}

.result-label {
    color: #aabaff;
    font-size: 13px;
}

.result-value {
    color: white;
    font-size: 27px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

div[data-testid="stTextInput"] input {
    background-color: #17223a;
    color: white;
    border: 1px solid #536baf;
    border-radius: 12px;
}

.stButton button {
    border-radius: 10px;
    font-weight: bold;
    min-height: 43px;
}

hr {
    border-color: #34415e;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "ans" not in st.session_state:
    st.session_state.ans = 0

if "angle" not in st.session_state:
    st.session_state.angle = "DEG"

# ---------- HEADER ----------
st.title("🧮 IZHAM CALCULATOR")
st.markdown(
    '<p class="subtitle">Advanced Scientific & Complex Calculator</p>',
    unsafe_allow_html=True
)

st.markdown("### ⚙️ Calculator Settings")

angle = st.radio(
    "Angle Mode",
    ["DEG", "RAD"],
    horizontal=True,
    index=0 if st.session_state.angle == "DEG" else 1
)
st.session_state.angle = angle

# ---------- MATH FUNCTIONS ----------
def trig(function):
    def calculate(x):
        if angle == "DEG":
            x = x * math.pi / 180
        return function(x)
    return calculate

def inverse_trig(function):
    def calculate(x):
        result = function(x)
        if angle == "DEG":
            result = result * 180 / math.pi
        return result
    return calculate

def safe_log(x, base=None):
    if base is None:
        return cmath.log(x)
    return cmath.log(x) / cmath.log(base)

def factorial(x):
    if isinstance(x, complex) and x.imag != 0:
        raise ValueError("Faktorial hanya menerima bilangan real")
    if x.real < 0 or not float(x.real).is_integer():
        raise ValueError("Faktorial harus bilangan bulat nonnegatif")
    if x.real > 170:
        raise ValueError("Angka terlalu besar")
    return math.factorial(int(x.real))

def real_part(x):
    return complex(x).real

def imag_part(x):
    return complex(x).imag

def conjugate(x):
    return complex(x).conjugate()

def power(a, b):
    if abs(b) > 1000:
        raise ValueError("Pangkat terlalu besar")
    return operator.pow(a, b)

FUNCTIONS = {
    "sin": trig(cmath.sin),
    "cos": trig(cmath.cos),
    "tan": trig(cmath.tan),
    "asin": inverse_trig(cmath.asin),
    "acos": inverse_trig(cmath.acos),
    "atan": inverse_trig(cmath.atan),
    "sqrt": cmath.sqrt,
    "log": safe_log,
    "ln": cmath.log,
    "log10": cmath.log10,
    "exp": cmath.exp,
    "abs": abs,
    "factorial": factorial,
    "real": real_part,
    "imag": imag_part,
    "conj": conjugate,
    "phase": cmath.phase,
}

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "i": 1j,
    "Ans": st.session_state.ans,
}

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: power,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# ---------- SAFE CALCULATOR ----------
def evaluate(node):
    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Input tidak valid")
        return node.value

    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ValueError("Konstanta tidak dikenal")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError("Operator tidak diizinkan")
        return OPERATORS[op_type](
            evaluate(node.left),
            evaluate(node.right)
        )

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in UNARY:
            raise ValueError("Operasi tidak diizinkan")
        return UNARY[op_type](evaluate(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Fungsi tidak valid")

        name = node.func.id
        if name not in FUNCTIONS or node.keywords:
            raise ValueError("Fungsi tidak dikenal")

        args = [evaluate(arg) for arg in node.args]
        return FUNCTIONS[name](*args)

    raise ValueError("Ekspresi tidak valid")

def calculate(expression):
    if not expression or len(expression) > 200:
        raise ValueError("Ekspresi kosong atau terlalu panjang")

    tree = ast.parse(expression, mode="eval")

    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError("Ekspresi terlalu kompleks")

    result = evaluate(tree.body)

    if isinstance(result, complex):
        if not math.isfinite(result.real) or not math.isfinite(result.imag):
            raise ValueError("Hasil tidak terhingga")
    elif not math.isfinite(result):
        raise ValueError("Hasil tidak terhingga")

    return result

# ---------- FORMAT RESULT ----------
def format_number(value):
    if isinstance(value, complex):
        real = 0 if abs(value.real) < 1e-12 else value.real
        imag = 0 if abs(value.imag) < 1e-12 else value.imag

        if imag == 0:
            return f"{real:.10g}"
        if real == 0:
            return f"{imag:.10g}i"

        sign = "+" if imag >= 0 else "-"
        return f"{real:.10g} {sign} {abs(imag):.10g}i"

    return f"{value:.12g}"

# ---------- INPUT ----------
st.markdown("---")
st.markdown("### 📝 Enter Expression")

expression = st.text_input(
    "Mathematical expression",
    placeholder="Contoh: sqrt(144) + sin(30)",
    key="expression"
)

st.caption(
    "Gunakan: +  -  *  /  **  %  ( )"
)

# ---------- BUTTONS ----------
col1, col2 = st.columns(2)

with col1:
    calculate_button = st.button(
        "🧮 CALCULATE",
        use_container_width=True
    )

with col2:
    clear_button = st.button(
        "🗑️ CLEAR",
        use_container_width=True
    )

if clear_button:
    st.session_state.history = []
    st.rerun()

if calculate_button:
    try:
        result = calculate(expression)

        st.session_state.ans = result
        formatted = format_number(result)

        st.markdown(
            f"""
            <div class="result">
                <div class="result-label">CALCULATION RESULT</div>
                <div class="result-value">{formatted}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.session_state.history.insert(
            0,
            {
                "expression": expression,
                "result": formatted
            }
        )

    except Exception as error:
        st.error(f"Calculation error: {error}")

# ---------- FUNCTION GUIDE ----------
st.markdown("---")
st.markdown("### 📚 Scientific Functions")

with st.expander("View function guide"):
    st.markdown("""
    | Function | Description |
    |---|---|
    | sin(x) | Sine |
    | cos(x) | Cosine |
    | tan(x) | Tangent |
    | asin(x) | Inverse sine |
    | acos(x) | Inverse cosine |
    | atan(x) | Inverse tangent |
    | sqrt(x) | Square root |
    | log(x) | Natural logarithm |
    | log10(x) | Logarithm basis 10 |
    | ln(x) | Natural logarithm |
    | exp(x) | Exponential |
    | factorial(x) | Factorial |
    | abs(x) | Absolute value |
    | real(x) | Real component |
    | imag(x) | Imaginary component |
    | conj(x) | Complex conjugate |
    | phase(x) | Complex argument |
    
    **Constants:** pi, e, i, Ans

    **Example expressions:**
    - sqrt(144)
    - sin(30)
    - log(100, 10)
    - 2**8
    - factorial(5)
    - 2+3*i
    - sqrt(-1)
    - abs(3+4*i)
    """)

# ---------- HISTORY ----------
st.markdown("---")
st.markdown("### 📜 Calculation History")

if st.session_state.history:
    for index, item in enumerate(st.session_state.history):
        st.markdown(
            f"**{index + 1}.** `{item['expression']}`"
            f" = **{item['result']}**"
        )
else:
    st.caption("No calculation history yet.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    '<div class="brand">MADE OF IZHAM • SCIENTIFIC CALCULATOR</div>',
    unsafe_allow_html=True
    )
