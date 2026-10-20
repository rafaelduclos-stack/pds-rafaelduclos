from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

BANCO = "petshop.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petshop.db"

db = SQLAlchemy(app)

class Dono(db.Model):
    __tablename__ = "donos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    pets = db.relationship("Pet", backref="dono")

    def to_dict(self):
        return{
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone
        }

class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    dono_id = db.Column(db.Integer, db.ForeignKey("donos.id"), nullable=False)

    def to_dict(self):
        return{
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "idade": self.idade,
            "dono_id": self.dono_id,
            "dono_nome": self.dono.nome
        }

@app.route("/donos", methods=["GET"])
def listar_donos():
    donos = Dono.query.all()
    return jsonify([dono.to_dict() for dono in donos])

@app.route("/donos/<int:dono_id>", methods=["GET"])
def buscar_dono(dono_id):
    dono = db.session.get(Dono, dono_id)

    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    return jsonify(dono.to_dict())

@app.route("/donos", methods=["POST"])
def criar_dono():
    dados = request.json

    if not dados or "nome" not in dados or "telefone" not in dados:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    novo_dono = Dono(nome=dados["nome"], telefone=dados["telefone"])

    db.session.add(novo_dono)
    db.session.commit()

    return jsonify(novo_dono.to_dict()), 201


@app.route("/donos/<int:dono_id>", methods=["PUT"])
def atualizar_dono(dono_id):
    dados = request.json

    if not dados or "nome" not in dados or "telefone" not in dados:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    dono = db.session.get(Dono, dono_id)

    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    dono.nome = dados["nome"]
    dono.telefone = dados["telefone"]
    db.session.commit()

    return jsonify(dono.to_dict())


@app.route("/donos/<int:dono_id>", methods=["DELETE"])
def remover_dono(dono_id):
    dono = db.session.get(Dono, dono_id)

    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    db.session.delete(dono)
    db.session.commit()

    return jsonify({"mensagem": "Dono removido com sucesso"})


@app.route("/pets", methods=["GET"])
def listar_pets():
    dono_id = request.args.get("dono_id", type=int)

    conexao = conectar()
    cursor = conexao.cursor()

    if dono_id is not None:
        cursor.execute("""
            SELECT
                pets.id,
                pets.nome,
                pets.especie,
                pets.idade,
                pets.dono_id,
                donos.nome
            FROM pets
            JOIN donos ON pets.dono_id = donos.id
            WHERE pets.dono_id = ?
        """, (dono_id,))
    else:
        cursor.execute("""
            SELECT
                pets.id,
                pets.nome,
                pets.especie,
                pets.idade,
                pets.dono_id,
                donos.nome
            FROM pets
            JOIN donos ON pets.dono_id = donos.id
        """)

    linhas = cursor.fetchall()
    conexao.close()

    pets = []

    for linha in linhas:
        pets.append({
            "id": linha[0],
            "nome": linha[1],
            "especie": linha[2],
            "idade": linha[3],
            "dono_id": linha[4],
            "dono_nome": linha[5]
        })

    return jsonify(pets)


@app.route("/pets/<int:id>", methods=["GET"])
def buscar_pet(id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            pets.id,
            pets.nome,
            pets.especie,
            pets.idade,
            pets.dono_id,
            donos.nome
        FROM pets
        JOIN donos ON pets.dono_id = donos.id
        WHERE pets.id = ?
    """, (id,))

    linha = cursor.fetchone()
    conexao.close()

    if linha is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    pet = {
        "id": linha[0],
        "nome": linha[1],
        "especie": linha[2],
        "idade": linha[3],
        "dono_id": linha[4],
        "dono_nome": linha[5]
    }

    return jsonify(pet), 200


@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.json

    if not dados or "nome" not in dados or "especie" not in dados or "idade" not in dados or "dono_id" not in dados:
        return jsonify({"erro": "Informe nome, especie, idade e dono_id"}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM donos WHERE id = ?",
        (dados["dono_id"],)
    )

    dono = cursor.fetchone()

    if dono is None:
        conexao.close()
        return jsonify({"erro": "Dono nao encontrado"}), 404

    cursor.execute(
        """
        INSERT INTO pets (nome, especie, idade, dono_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            dados["nome"],
            dados["especie"],
            dados["idade"],
            dados["dono_id"]
        )
    )

    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()

    pet = {
        "id": novo_id,
        "nome": dados["nome"],
        "especie": dados["especie"],
        "idade": dados["idade"],
        "dono_id": dados["dono_id"]
    }

    return jsonify(pet), 201


@app.route("/pets/<int:id>", methods=["PUT"])
def atualizar_pet(id):
    dados = request.json

    if not dados or "nome" not in dados or "especie" not in dados or "idade" not in dados or "dono_id" not in dados:
        return jsonify({"erro": "Informe nome, especie, idade e dono_id"}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM donos WHERE id = ?",
        (dados["dono_id"],)
    )

    dono = cursor.fetchone()

    if dono is None:
        conexao.close()
        return jsonify({"erro": "Dono nao encontrado"}), 404

    cursor.execute(
        """
        UPDATE pets
        SET nome = ?, especie = ?, idade = ?, dono_id = ?
        WHERE id = ?
        """,
        (
            dados["nome"],
            dados["especie"],
            dados["idade"],
            dados["dono_id"],
            id
        )
    )

    conexao.commit()
    alterados = cursor.rowcount
    conexao.close()

    if alterados == 0:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    pet = {
        "id": id,
        "nome": dados["nome"],
        "especie": dados["especie"],
        "idade": dados["idade"],
        "dono_id": dados["dono_id"]
    }

    return jsonify(pet)


@app.route("/pets/<int:id>", methods=["DELETE"])
def remover_pet(id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM pets WHERE id = ?",
        (id,)
    )

    conexao.commit()
    removidos = cursor.rowcount
    conexao.close()

    if removidos == 0:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    return jsonify({"mensagem": "Pet removido com sucesso"})


if __name__ == "__main__":
    app.run(debug=True)
