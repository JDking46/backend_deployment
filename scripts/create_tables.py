from db.session import engine, Base

if __name__ == "__main__":
    # Creates missing tables/columns based on models
    Base.metadata.create_all(bind=engine)
    print("Database tables created/updated (if supported by the DB).")
