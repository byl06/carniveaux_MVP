from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Chantier(Base):
    __tablename__ = "chantiers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(200), nullable=False)
    localisation = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    troncons = relationship("Troncon", back_populates="chantier", cascade="all, delete-orphan")


class Troncon(Base):
    __tablename__ = "troncons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False)
    reference = Column(String(100), nullable=False)
    longueur = Column(Float, nullable=False)
    largeur = Column(Float)
    hauteur = Column(Float)
    epaisseur_radier = Column(Float)
    epaisseur_paroi = Column(Float)
    largeur_fouille = Column(Float)
    profondeur_fouille = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    chantier = relationship("Chantier", back_populates="troncons")


class Materiau(Base):
    __tablename__ = "materiaux"
    id = Column(Integer, primary_key=True, autoincrement=True)
    designation = Column(String(100), nullable=False)
    unite = Column(String(20), nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompositionBeton(Base):
    __tablename__ = "compositions_beton"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False)
    materiau_id = Column(Integer, ForeignKey("materiaux.id"), nullable=False)
    quantite_par_m3 = Column(Float, nullable=False)
    reference_validation = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


class Depense(Base):
    __tablename__ = "depenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False)
    categorie = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    montant = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Avancement(Base):
    __tablename__ = "avancements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    troncon_id = Column(Integer, ForeignKey("troncons.id", ondelete="CASCADE"), nullable=False)
    etape = Column(String(50), nullable=False)
    statut = Column(String(30), nullable=False, default="non commencé")
    date = Column(DateTime, default=datetime.utcnow)
    observation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)