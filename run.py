from gazetteer.app import config_app

# A mettre à jour

if __name__ == "__main__":
    app = config_app("production")
    app.run(debug=True)
