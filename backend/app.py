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
    pets = Pet.query.all()
    return jsonify([pet.to_dict() for pet in pets])


@app.route("/pets/<int:pet.id>", methods=["GET"])
def buscar_pet(id):
    pet = db.session.get(Pet, pet.id)

    if pet is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    return jsonify(pet.to_dict())
        


if __name__ == "__main__":
    app.run(debug=True)
