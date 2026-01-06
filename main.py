from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import sqlite3
from pathlib import Path

#Banco de dados
#DB_PATH = Path("financeiro.db")
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "financeiro.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpf TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor REAL NOT NULL,
    descricao TEXT NOT NULL
)
""")

conn.commit()

#Guardrails
class Transacao(BaseModel):
    cpf: str
    tipo: str
    valor: float
    descricao: str

    @field_validator("cpf")
    @classmethod
    def cpf_valido(cls, v):
        v = v.replace(".", "").replace("-", "")
        if not v.isdigit() or len(v) != 11:
            raise ValueError("CPF inválido")
        return v

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        tipos_permitidos = ["pix", "ted", "doc", "boleto"]
        if v.lower() not in tipos_permitidos:
            raise ValueError("Tipo de transação não permitido")
        return v.lower()

    @field_validator("valor")
    @classmethod
    def valor_valido(cls, v):
        if v <= 0:
            raise ValueError("Valor deve ser positivo")
        if v > 100_000:
            raise ValueError("Valor acima do limite permitido")
        return v

    @field_validator("descricao")
    @classmethod
    def descricao_valida(cls, v):
        if len(v.strip()) < 5:
            raise ValueError("Descrição muito curta")
        return v
      

#App
app = FastAPI(title="API Financeira com Guardrails")

#endpoints
#home
@app.get("/")
def home():
    return {"mensagem": "Sistema financeiro seguro"}

#endpoints
#Cadastrar transação 
@app.post("/transacoes")
def criar_transacao(t: Transacao):
    cursor.execute(
        "INSERT INTO transacoes (cpf, tipo, valor, descricao) VALUES (?, ?, ?, ?)",
        (t.cpf, t.tipo, t.valor, t.descricao)
    )
    conn.commit()
    return {"mensagem": "Transação registrada com sucesso"}

#endpoint
#Listrar transações
@app.get("/transacoes")
def listar_transacoes():
    cursor.execute("SELECT id, cpf, tipo, valor, descricao FROM transacoes")
    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "cpf": r[1],
            "tipo": r[2],
            "valor": r[3],
            "descricao": r[4]
        }
        for r in rows
    ]

@app.get("/status")
def status():
    return {"status": "API financeira ativa"}







