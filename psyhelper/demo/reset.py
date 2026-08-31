from .seed import seed_demo_database, DEFAULT_DB

def reset_demo_database(path=DEFAULT_DB):
    return seed_demo_database(path)

if __name__=="__main__": reset_demo_database()
