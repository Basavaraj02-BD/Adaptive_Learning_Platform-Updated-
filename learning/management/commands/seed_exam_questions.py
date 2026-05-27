from django.core.management.base import BaseCommand
from learning.models import Exam, Question
import json

class Command(BaseCommand):
    help = "Seed the database to ensure all exams have at least 10 questions."

    def handle(self, *args, **kwargs):
        # Map keywords to specific question pools
        # Format: (question_text, question_type, options_list, correct_answer, explanation, difficulty, marks)
        
        python_questions = [
            ("Which of the following is a mutable data type in Python?", "mcq", ["List", "Tuple", "String", "Integer"], "List", "Lists can be modified in place, unlike tuples, strings, or ints.", "easy", 2),
            ("What is the output of '2 ** 3' in Python?", "mcq", ["6", "8", "9", "5"], "8", "** is the exponentiation operator in Python.", "easy", 2),
            ("How do you start a generator function in Python?", "mcq", ["Using the 'generator' keyword", "Using the 'return' keyword", "Using the 'yield' keyword", "Using the 'next' keyword"], "Using the 'yield' keyword", "Generator functions return an iterator that yields items one at a time using 'yield'.", "medium", 2),
            ("Which keyword is used for exception handling in Python?", "mcq", ["try-catch", "try-except", "handle-error", "try-finally"], "try-except", "Python uses try-except blocks to catch and handle exceptions.", "easy", 2),
            ("What is list comprehension in Python?", "mcq", ["A way to understand list data", "A concise syntax for creating lists from iterables", "A method to compress lists", "A function to sort lists"], "A concise syntax for creating lists from iterables", "List comprehensions offer a shorter syntax to create a new list based on existing lists.", "medium", 2),
            ("What does the 'self' keyword represent in Python class methods?", "mcq", ["The class itself", "A global variable", "The instance of the class", "The parent class"], "The instance of the class", "self represents the current instance of the class.", "easy", 2),
            ("Which method is used to add an element to the end of a list?", "mcq", ["add()", "insert()", "append()", "push()"], "append()", "append() adds an item to the end of a list.", "easy", 2),
            ("What is the purpose of '__init__' in Python?", "mcq", ["To initialize a list", "Constructor method to initialize a new instance", "To import modules", "To terminate a class"], "Constructor method to initialize a new instance", "__init__ is the constructor method in Python classes.", "easy", 2),
            ("Which of the following is NOT a built-in data type in Python?", "mcq", ["Set", "Dictionary", "Array", "Tuple"], "Array", "Python has built-in lists, tuples, dictionaries, and sets, but 'Array' requires importing the array module.", "medium", 2),
            ("In Python, dictionaries are indexed by keys.", "true_false", [], "True", "Dictionary keys must be immutable types (like strings, numbers, or tuples).", "easy", 2),
            ("Does Python support multiple inheritance?", "true_false", [], "True", "Yes, Python classes can inherit from multiple parent classes.", "medium", 2),
            ("What is the output of 'type(lambda x: x)' in Python?", "mcq", ["<class 'function'>", "<class 'lambda'>", "<class 'object'>", "Error"], "<class 'function'>", "A lambda expression creates a function object.", "hard", 2),
        ]

        django_questions = [
            ("Which command is used to apply migrations in Django?", "mcq", ["python manage.py makemigrations", "python manage.py migrate", "python manage.py runserver", "python manage.py db_migrate"], "python manage.py migrate", "migrate runs the pending migrations to update the database schema.", "easy", 2),
            ("In Django's MVT pattern, what does 'V' stand for?", "mcq", ["Volume", "Variable", "View", "Vector"], "View", "View handles business logic and responds to client requests.", "easy", 2),
            ("Which file is used to configure URLs in a Django application?", "mcq", ["settings.py", "views.py", "models.py", "urls.py"], "urls.py", "urls.py maps URLs to views.", "easy", 2),
            ("What does the Django ORM stand for?", "mcq", ["Object Relational Mapping", "Object Runtime Manager", "Operational Resource Model", "Object Routing Map"], "Object Relational Mapping", "ORM translates database rows into Python objects.", "easy", 2),
            ("How do you render a context variable 'title' inside a Django template?", "mcq", ["{ title }", "{{ title }}", "{% title %}", "[[ title ]]"], "{{ title }}", "Double curly braces are used to display variables in templates.", "easy", 2),
            ("Which Django model field is used to represent a many-to-one relationship?", "mcq", ["ManyToManyField", "OneToOneField", "ForeignKey", "ManyToOneField"], "ForeignKey", "ForeignKey represents a many-to-one relationship in Django.", "medium", 2),
            ("What is the primary purpose of Django middleware?", "mcq", ["To render HTML pages", "To process requests and responses globally", "To connect to external databases", "To design forms"], "To process requests and responses globally", "Middleware is a framework of hooks into Django's request/response processing.", "medium", 2),
            ("Django templates can execute arbitrary Python code.", "true_false", [], "False", "Django template language intentionally restricts executing arbitrary Python code for security and separation of concerns.", "easy", 2),
            ("Where are database credentials configured in a Django project?", "mcq", ["models.py", "urls.py", "settings.py", "views.py"], "settings.py", "Database settings are defined in the DATABASES setting within settings.py.", "easy", 2),
            ("What does 'makemigrations' command do?", "mcq", ["Applies migrations to DB", "Creates new migration files based on model changes", "Creates database tables", "Deletes existing migrations"], "Creates new migration files based on model changes", "makemigrations creates new migrations based on the changes detected in models.", "easy", 2),
            ("Which decorator is used to restrict view access to logged-in users?", "mcq", ["@login_required", "@user_logged_in", "@authenticated", "@auth_check"], "@login_required", "The @login_required decorator checks if the user is authenticated.", "easy", 2),
        ]

        html_questions = [
            ("Which tag is used to create a hyperlink in HTML?", "mcq", ["<link>", "<a>", "<href>", "<url>"], "<a>", "The <a> (anchor) tag is used to define hyperlinks.", "easy", 2),
            ("What does HTML stand for?", "mcq", ["Hyper Text Markup Language", "Home Tool Markup Language", "Hyperlinks and Text Markup Language", "High Text Machine Language"], "Hyper Text Markup Language", "HTML is the standard markup language for web documents.", "easy", 2),
            ("Which is the correct HTML element for the largest heading?", "mcq", ["<h6>", "<heading>", "<h1>", "<head>"], "<h1>", "<h1> defines the most important and largest heading.", "easy", 2),
            ("What is the correct HTML for adding a background color?", "mcq", ["<body bg=\"yellow\">", "<body style=\"background-color:yellow;\">", "<background>yellow</background>", "<body color=\"yellow\">"], "<body style=\"background-color:yellow;\">", "Inline CSS style is used to specify background color in modern HTML.", "medium", 2),
            ("Which HTML tag is used to define an unordered list?", "mcq", ["<ol>", "<ul>", "<li>", "<list>"], "<ul>", "<ul> is used for unordered lists (bulleted).", "easy", 2),
            ("What is the correct HTML element for inserting a line break?", "mcq", ["<break>", "<lb>", "<br>", "<next>"], "<br>", "<br> inserts a single line break.", "easy", 2),
            ("Which attribute specifies an alternate text for an image if it cannot be displayed?", "mcq", ["title", "alt", "src", "longdesc"], "alt", "The 'alt' attribute provides alternative text for images.", "easy", 2),
            ("An <iframe> is used to display a web page within a web page.", "true_false", [], "True", "Yes, iframe stands for inline frame, used to embed another document.", "easy", 2),
            ("Which HTML5 element is used to display visual illustrations/diagrams dynamically?", "mcq", ["<canvas>", "<picture>", "<svg>", "<display>"], "<canvas>", "The <canvas> element is used to draw graphics on the fly via scripting (usually JavaScript).", "medium", 2),
            ("In HTML, inline elements start on a new line by default.", "true_false", [], "False", "Block-level elements start on a new line; inline elements do not.", "easy", 2),
            ("What is the correct HTML element for playing audio files?", "mcq", ["<sound>", "<music>", "<audio>", "<play>"], "<audio>", "HTML5 introduced the <audio> tag for audio playback.", "easy", 2),
        ]

        css_questions = [
            ("What does CSS stand for?", "mcq", ["Creative Style Sheets", "Computer Style Sheets", "Cascading Style Sheets", "Colorful Style Sheets"], "Cascading Style Sheets", "CSS defines how HTML elements are to be displayed.", "easy", 2),
            ("Which HTML attribute is used to reference an external CSS file?", "mcq", ["<style>", "<link>", "<css>", "<meta>"], "<link>", "<link rel=\"stylesheet\" href=\"styles.css\"> is used to link CSS files.", "easy", 2),
            ("Where in an HTML document is the correct place to refer to an external style sheet?", "mcq", ["In the <body> section", "At the end of the document", "In the <head> section", "Directly in the tags"], "In the <head> section", "External style sheets are referenced inside the <head> section.", "easy", 2),
            ("Which CSS property is used to change the text color of an element?", "mcq", ["fgcolor", "text-color", "color", "font-color"], "color", "The 'color' property specifies the color of the text.", "easy", 2),
            ("Which CSS property controls the text size?", "mcq", ["font-style", "text-style", "font-size", "text-size"], "font-size", "The 'font-size' property sets the size of the font.", "easy", 2),
            ("How do you select an element with id 'demo' in CSS?", "mcq", [".demo", "#demo", "demo", "*demo"], "#demo", "Hash (#) selector is used for selecting IDs.", "easy", 2),
            ("How do you select elements with class name 'test' in CSS?", "mcq", ["#test", ".test", "test", "*test"], ".test", "Dot (.) selector is used for selecting classes.", "easy", 2),
            ("What is the default value of the position property in CSS?", "mcq", ["relative", "absolute", "static", "fixed"], "static", "HTML elements are positioned static by default.", "medium", 2),
            ("In the box model, margin is inside the border.", "true_false", [], "False", "Margin is outside the border; padding is inside the border.", "easy", 2),
            ("Which CSS property is used to set the spacing between grid items?", "mcq", ["grid-gap", "gap", "margin", "padding"], "gap", "'gap' (formerly grid-gap) sets the gaps between rows and columns.", "medium", 2),
            ("What does 'box-sizing: border-box' do?", "mcq", ["Includes padding and border in total width/height", "Excludes padding and border", "Sets border color", "None"], "Includes padding and border in total width/height", "border-box includes padding and border in width and height calculations.", "medium", 2),
        ]

        js_questions = [
            ("Which of the following is correct to write 'Hello World' on the web page using JS?", "mcq", ["document.write('Hello World')", "response.write('Hello World')", "print('Hello World')", "system.out.println('Hello World')"], "document.write('Hello World')", "document.write() writes directly to the HTML document stream.", "easy", 2),
            ("How do you declare a JavaScript variable?", "mcq", ["var name;", "variable name;", "v name;", "declare name;"], "var name;", "JS uses var, let, or const to declare variables.", "easy", 2),
            ("Which operator is used to assign a value to a variable?", "mcq", ["*", "-", "=", "=="], "=", "= is the assignment operator in JS.", "easy", 2),
            ("What is the output of 'typeof []' in JavaScript?", "mcq", ["'array'", "'object'", "'list'", "'undefined'"], "'object'", "Arrays are a special type of object in JS.", "medium", 2),
            ("Which method is used to add an element at the end of an array in JS?", "mcq", ["push()", "pop()", "shift()", "unshift()"], "push()", "push() adds one or more elements to the end of an array.", "easy", 2),
            ("How do you select an element by its ID in JS?", "mcq", ["document.getElement('id')", "document.getElementById('id')", "document.queryId('id')", "document.find('id')"], "document.getElementById('id')", "getElementById selects an element by its unique ID attribute.", "easy", 2),
            ("What is a closure in JavaScript?", "mcq", ["A function enclosed in another function", "A function combined with its lexical environment", "Closing a database connection", "None"], "A function combined with its lexical environment", "A closure gives you access to an outer function's scope from an inner function.", "hard", 2),
            ("JavaScript is single-threaded.", "true_false", [], "True", "JS runs on a single main thread, using an event loop for concurrency.", "medium", 2),
            ("Which keyword is used to handle asynchronous code in ES8?", "mcq", ["promise", "async/await", "then", "defer"], "async/await", "async/await syntax allows writing asynchronous code synchronously.", "medium", 2),
            ("Which event occurs when the user clicks on an HTML element?", "mcq", ["onchange", "onclick", "onmouseover", "onclickpage"], "onclick", "onclick is the click event listener in JS.", "easy", 2),
            ("What does 'NaN' stand for in JavaScript?", "mcq", ["Not a Number", "New and Null", "Null and Negated", "None"], "Not a Number", "NaN represents a value that is not a valid number.", "easy", 2),
        ]

        dsa_questions = [
            ("What is the time complexity of searching in a sorted array using binary search?", "mcq", ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "O(log n)", "Binary search halves the search space at each iteration.", "easy", 2),
            ("Which data structure operates on a Last In First Out (LIFO) basis?", "mcq", ["Queue", "Stack", "Linked List", "Tree"], "Stack", "Stacks use LIFO where the last element inserted is the first removed.", "easy", 2),
            ("Which data structure operates on a First In First Out (FIFO) basis?", "mcq", ["Stack", "Queue", "Binary Tree", "Heap"], "Queue", "Queues use FIFO where the first element inserted is the first removed.", "easy", 2),
            ("What is the worst-case time complexity of Quick Sort?", "mcq", ["O(n log n)", "O(n²)", "O(n)", "O(2^n)"], "O(n²)", "Quick Sort exhibits O(n²) worst-case complexity if the pivot selection is poor.", "medium", 2),
            ("What is a binary search tree (BST)?", "mcq", ["A tree where each node has exactly 2 children", "A tree where left child <= parent and right child > parent", "A tree where all operations are O(1)", "None"], "A tree where left child <= parent and right child > parent", "BST maintains ordered properties for efficient search.", "medium", 2),
            ("Which algorithm is used to find the shortest path in a weighted graph?", "mcq", ["Kruskal's", "Dijkstra's", "Prim's", "Depth First Search"], "Dijkstra's", "Dijkstra's algorithm computes single-source shortest paths in weighted graphs.", "medium", 2),
            ("A linked list stores elements in contiguous memory locations.", "true_false", [], "False", "No, array elements are contiguous; linked lists use pointers to connect nodes.", "easy", 2),
            ("What is the time complexity of inserting an item at the beginning of a Singly Linked List?", "mcq", ["O(1)", "O(n)", "O(log n)", "O(n²)"], "O(1)", "Inserting at head requires only updating pointers, which is O(1).", "medium", 2),
            ("Which of the following is a non-linear data structure?", "mcq", ["Stack", "Array", "Graph", "Queue"], "Graph", "Graphs and Trees are non-linear; others are linear.", "easy", 2),
            ("What does 'Big O' notation measure?", "mcq", ["The exact execution time of a program", "The worst-case complexity of an algorithm", "The code quality", "Memory size of a structure"], "The worst-case complexity of an algorithm", "Big O describes the upper bound of running time or space requirements.", "easy", 2),
            ("Which sorting algorithm has a guaranteed worst-case time complexity of O(n log n)?", "mcq", ["Bubble Sort", "Insertion Sort", "Merge Sort", "Quick Sort"], "Merge Sort", "Merge Sort consistently divides lists and runs in O(n log n) time.", "medium", 2),
        ]

        ml_questions = [
            ("Which of the following is a type of supervised learning?", "mcq", ["Clustering", "Regression", "Dimensionality Reduction", "Association Rule Mining"], "Regression", "Regression maps inputs to continuous outputs using labelled data.", "easy", 2),
            ("What is overfitting?", "mcq", ["Model performs poorly on both train and test data", "Model performs well on train data but poorly on test data", "Model generalizes well to new data", "None"], "Model performs well on train data but poorly on test data", "Overfitting occurs when a model fits noise in the training set.", "easy", 2),
            ("What is the purpose of an activation function in neural networks?", "mcq", ["To initialize weights", "To introduce non-linearity", "To compute gradients", "To reduce learning rate"], "To introduce non-linearity", "Activation functions allow neural networks to learn non-linear patterns.", "medium", 2),
            ("Which of the following is a classification algorithm?", "mcq", ["Linear Regression", "Logistic Regression", "K-Means", "PCA"], "Logistic Regression", "Despite its name, Logistic Regression is used for binary classification.", "easy", 2),
            ("What is the primary goal of unsupervised learning?", "mcq", ["Predict continuous values", "Find hidden patterns or structures in unlabelled data", "Map inputs to labels", "Maximize rewards in an environment"], "Find hidden patterns or structures in unlabelled data", "Unsupervised learning works on unlabelled data to group or cluster items.", "easy", 2),
            ("What does PCA stand for in machine learning?", "mcq", ["Primary Component Analysis", "Principal Component Analysis", "Predictive Coding Algorithm", "None"], "Principal Component Analysis", "PCA is a dimensionality reduction technique.", "medium", 2),
            ("Gradient Descent is used to minimize the loss function.", "true_false", [], "True", "Gradient descent updates parameters iteratively to find the minimum of a cost function.", "easy", 2),
            ("Which metric is most sensitive to outliers in regression tasks?", "mcq", ["Mean Absolute Error (MAE)", "Mean Squared Error (MSE)", "R-squared", "None"], "Mean Squared Error (MSE)", "MSE squares errors, heavily penalizing large outliers.", "medium", 2),
            ("What is reinforcement learning?", "mcq", ["Training on labeled image data", "Learning through trial-and-error rewards and punishments", "Reducing dimensions of tabular data", "Clustering similar documents"], "Learning through trial-and-error rewards and punishments", "Reinforcement learning optimizes actions of agents in environments.", "easy", 2),
            ("In artificial neural networks, backpropagation computes the gradient of the loss function.", "true_false", [], "True", "Backpropagation computes the gradient of the loss with respect to weights using the chain rule.", "medium", 2),
            ("Which of the following is an ensemble learning method?", "mcq", ["Decision Tree", "Random Forest", "Support Vector Machine", "Naive Bayes"], "Random Forest", "Random Forest uses bagging to combine multiple decision trees.", "medium", 2),
        ]

        sql_questions = [
            ("Which SQL clause is used to filter records?", "mcq", ["GROUP BY", "WHERE", "ORDER BY", "SELECT"], "WHERE", "WHERE filters rows matching conditions.", "easy", 2),
            ("Which JOIN returns all records when there is a match in either left or right table?", "mcq", ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"], "FULL JOIN", "FULL OUTER JOIN returns all rows from both tables.", "medium", 2),
            ("What is a primary key?", "mcq", ["A key that allows duplicate values", "A column that uniquely identifies each row in a table", "A key that links to another table", "None"], "A column that uniquely identifies each row in a table", "Primary keys uniquely identify rows and cannot contain NULL values.", "easy", 2),
            ("Which SQL statement is used to insert new records in a database?", "mcq", ["ADD NEW", "INSERT INTO", "ADD RECORD", "CREATE ROW"], "INSERT INTO", "INSERT INTO is the standard DML statement.", "easy", 2),
            ("What is the purpose of the GROUP BY statement?", "mcq", ["Sort rows alphabetically", "Group rows that have the same values into summary rows", "Filter output values", "None"], "Group rows that have the same values into summary rows", "GROUP BY is used with aggregate functions to group rows.", "easy", 2),
            ("The HAVING clause is used instead of WHERE when filtering groups.", "true_false", [], "True", "HAVING filters groups created by GROUP BY; WHERE filters individual rows.", "medium", 2),
            ("Which command removes all rows from a table without logging individual row deletions?", "mcq", ["DELETE", "DROP", "TRUNCATE", "REMOVE"], "TRUNCATE", "TRUNCATE is a DDL command that quickly empties a table.", "hard", 2),
            ("What is a foreign key?", "mcq", ["A key used to encrypt tables", "A column that references the primary key of another table", "A key from an external database link", "None"], "A column that references the primary key of another table", "Foreign keys establish relationships between tables.", "easy", 2),
            ("Which SQL function is used to count the number of rows?", "mcq", ["SUM()", "COUNT()", "NUMBER()", "TOTAL()"], "COUNT()", "COUNT() returns the number of rows.", "easy", 2),
            ("Indices speed up data retrieval but slow down updates.", "true_false", [], "True", "Yes, indices speed up SELECT queries but add overhead for INSERT/UPDATE/DELETE.", "medium", 2),
            ("What does SQL stand for?", "mcq", ["Structured Query Language", "Simple Query Language", "Sequential Query Language", "Standard Query Language"], "Structured Query Language", "SQL is the standard language for relational databases.", "easy", 2),
        ]

        c_questions = [
            ("Which operator is used to get the address of a variable in C?", "mcq", ["*", "&", "#", "$"], "&", "The address-of operator & returns the memory address.", "easy", 2),
            ("What is the size of an int data type in C on typical 32/64 bit systems?", "mcq", ["1 byte", "2 bytes", "4 bytes", "8 bytes"], "4 bytes", "Typically, int is 4 bytes on modern systems.", "easy", 2),
            ("Which function is used to allocate memory dynamically in C?", "mcq", ["alloc()", "malloc()", "create()", "new()"], "malloc()", "malloc() allocates specified bytes of memory from heap.", "easy", 2),
            ("What is a pointer in C?", "mcq", ["A variable that stores a value", "A variable that stores the memory address of another variable", "An operator", "A compiler flag"], "A variable that stores the memory address of another variable", "Pointers hold address values.", "easy", 2),
            ("Which keyword is used to define a structure in C?", "mcq", ["struct", "class", "structure", "define"], "struct", "struct declares a user-defined compound type.", "easy", 2),
            ("In C, array indices start at 1.", "true_false", [], "False", "Arrays are 0-indexed in C.", "easy", 2),
            ("Which function is used to free dynamically allocated memory in C?", "mcq", ["dealloc()", "delete()", "free()", "release()"], "free()", "free() deallocates memory allocated by malloc/calloc/realloc.", "easy", 2),
            ("What is the output of '5 / 2' in integer division in C?", "mcq", ["2.5", "2", "3", "Error"], "2", "Integer division truncates decimal parts.", "easy", 2),
            ("What is the purpose of the '#include' preprocessor directive?", "mcq", ["To compile code", "To insert the contents of a header file", "To declare variables", "None"], "To insert the contents of a header file", "#include imports standard or user-defined headers.", "easy", 2),
            ("Which of the following is NOT a storage class in C?", "mcq", ["auto", "register", "static", "dynamic"], "dynamic", "The storage classes in C are auto, register, static, and extern.", "medium", 2),
            ("What character terminates all strings in C?", "mcq", ["\\n", "\\t", "\\0", ";"], "\\0", "C strings are null-terminated sequences of characters.", "easy", 2),
        ]

        java_questions = [
            ("Which component is responsible for executing Java bytecode?", "mcq", ["JDK", "JRE", "JVM", "JIT"], "JVM", "JVM (Java Virtual Machine) executes the bytecode.", "easy", 2),
            ("Which class is the superclass of all classes in Java?", "mcq", ["String", "Object", "Class", "System"], "Object", "Object class is the root of the class hierarchy.", "easy", 2),
            ("Which keyword is used to prevent method overriding in Java?", "mcq", ["static", "final", "abstract", "const"], "final", "A final method cannot be overridden by subclasses.", "easy", 2),
            ("What is the default value of a local variable in Java?", "mcq", ["0", "null", "Garbage value", "None (Must be initialized)"], "None (Must be initialized)", "Local variables must be explicitly initialized before use.", "medium", 2),
            ("Java support multiple inheritance of classes.", "true_false", [], "False", "Java does not support multiple inheritance of classes to prevent the diamond problem, but supports multiple inheritance of interfaces.", "easy", 2),
            ("Which keyword is used to create an object in Java?", "mcq", ["create", "new", "init", "make"], "new", "new allocates memory and invokes constructors.", "easy", 2),
            ("Which package is imported by default in every Java program?", "mcq", ["java.util", "java.io", "java.lang", "java.net"], "java.lang", "java.lang package is implicitly imported.", "easy", 2),
            ("What does JRE stand for?", "mcq", ["Java Runtime Environment", "Java Running Engine", "Java Rapid Execution", "None"], "Java Runtime Environment", "JRE includes JVM and class libraries to run applications.", "easy", 2),
            ("An interface in Java can have private methods (Java 9+).", "true_false", [], "True", "Yes, Java 9 introduced private methods in interfaces for helper logic.", "medium", 2),
            ("Which collection class allows unique elements only?", "mcq", ["ArrayList", "LinkedList", "HashSet", "Vector"], "HashSet", "HashSet implements Set interface, holding unique values.", "easy", 2),
            ("What is the size of 'char' data type in Java?", "mcq", ["1 byte", "2 bytes", "4 bytes", "Depends on OS"], "2 bytes", "Java uses UTF-16 representation, making char 2 bytes.", "medium", 2),
        ]

        # Map keywords in exam names to question pools
        mapping = {
            "python": python_questions,
            "django": django_questions,
            "html": html_questions,
            "css": css_questions,
            "javascript": js_questions,
            "js": js_questions,
            "data structures": dsa_questions,
            "dsa": dsa_questions,
            "machine learning": ml_questions,
            "artificial intelligence": ml_questions,
            "sql": sql_questions,
            "c programming": c_questions,
            "java": java_questions,
            "web development": js_questions + html_questions,  # Combine JS and HTML for general web development
        }

        self.stdout.write(self.style.MIGRATE_HEADING("Starting seeding of exam questions..."))
        
        exams = Exam.objects.all()
        for exam in exams:
            self.stdout.write(f"Processing Exam: '{exam.title}' (Course: {exam.course.title})")
            
            # Find matching pool
            title_lower = exam.title.lower()
            pool = None
            for key, q_pool in mapping.items():
                if key in title_lower:
                    pool = q_pool
                    break
            
            if not pool:
                # Fall back to Python questions if no direct match is found
                pool = python_questions
                self.stdout.write(f"  Warning: No direct pool matched '{exam.title}'. Using Python questions.")

            # Check current questions count
            current_count = exam.questions.count()
            self.stdout.write(f"  Current count: {current_count} questions.")
            
            if current_count >= 10:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Exam already has {current_count} questions."))
                continue

            # Add questions from pool until we hit 10
            needed = 10 - current_count
            added = 0
            
            # Loop through the pool and insert non-duplicate questions
            # Check text to avoid double insertion
            existing_texts = [q.question_text.lower().strip() for q in exam.questions.all()]
            
            for q_data in pool:
                if added >= needed:
                    break
                
                text, q_type, options, correct, explanation, diff, marks = q_data
                if text.lower().strip() in existing_texts:
                    continue
                
                # Create question
                q = Question.objects.create(
                    exam=exam,
                    question_text=text,
                    question_type=q_type,
                    correct_answer=correct,
                    explanation=explanation,
                    difficulty=diff,
                    marks=marks,
                    order=current_count + added + 1
                )
                if options:
                    q.set_options(options)
                    q.save()
                    
                added += 1
                existing_texts.append(text.lower().strip())
                
            self.stdout.write(self.style.SUCCESS(f"  [OK] Added {added} questions. Total: {exam.questions.count()}"))
            
            # Update total marks of the exam
            total_marks = sum(q.marks for q in exam.questions.all())
            exam.total_marks = total_marks
            # Recalculate pass marks (40% of total)
            exam.pass_marks = int(total_marks * 0.4)
            exam.save()
            self.stdout.write(f"  Updated total_marks to {total_marks}, pass_marks to {exam.pass_marks}.")

        self.stdout.write(self.style.SUCCESS("All exams have at least 10 questions successfully seeded."))
