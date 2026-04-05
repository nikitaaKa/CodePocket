import random
from data import db_session
from data.__all_models import User, Language, Topic, Library, CodeSnippet

LANGS_CONTENT = {
    "Python": "def hello():\n    print('Hello from Python!')",
    "JavaScript": "function hello() {\n    console.log('Hello from JS');\n}",
    "C++": "int main() {\n    std::cout << \"Hello C++\";\n    return 0;\n}",
    "Java": "public class Main {\n    public static void main(String[] args) {}\n}",
    "Go": "func main() {\n    fmt.Println(\"Hello Go\")\n}"
}

def fill_db():
    db_session.global_init("db/data.db")
    db_sess = db_session.create_session()

    users = []
    for i in range(1, 4):
        user = User(username=f"Developer_{i}", email=f"dev{i}@test.com", creator=True)
        user.set_password("1234")
        db_sess.add(user)
        users.append(user)
    
    db_sess.commit()

    user_index = 0
    
    for lang_name, code_sample in LANGS_CONTENT.items():
        lang = Language(name=lang_name)
        db_sess.add(lang)
        db_sess.flush()

        for t in range(1, 4):
            topic = Topic(name=f"Theme {t} for {lang_name}", language=lang)
            db_sess.add(topic)
            db_sess.flush()

            for l in range(1, 4):
                lib = Library(name=f"Lib_{lang_name}_{t}_{l}", topic=topic)
                db_sess.add(lib)
                db_sess.flush()

                for s in range(1, 7):
                    current_user = users[user_index % len(users)]
                    
                    snippet = CodeSnippet(
                        title=f"Snippet {s} for {lib.name}",
                        content=f"// Example {s}\n{code_sample}",
                        library=lib,
                        user=current_user
                    )

                    current_user.publications = (current_user.publications or 0) + 1
                    
                    db_sess.add(snippet)
                    user_index += 1

    db_sess.commit()
    print(f"Готово! Создано {len(LANGS_CONTENT)} языков и распределено {user_index} сниппетов.")

if __name__ == '__main__':
    fill_db()
