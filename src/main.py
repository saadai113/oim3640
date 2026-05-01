from crew import Oim3640Crew


def run():
    inputs = {
        'code': open('../code/hello.py').read(),
        'student_name': 'Student',
        'filename': 'hello.py',
    }
    result = Oim3640Crew().crew().kickoff(inputs=inputs)
    print(result)
    return result


if __name__ == "__main__":
    run()
