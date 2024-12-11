class University:
    def __init__(self, name, departments):
        self.name = name
        self.departments = departments  # List of Department objects

    def get_departments(self):
        return [dept.get_name() for dept in self.departments]

    def find_professor(self, prof_name):
        for dept in self.departments:
            prof = dept.find_professor(prof_name)
            if prof:
                return f"Professor {prof_name} found in {dept.get_name()}"
        return f"Professor {prof_name} not found"


class Department:
    def __init__(self, name, professors):
        self.name = name
        self.professors = professors  # List of Professor objects

    def get_name(self):
        return self.name

    def find_professor(self, prof_name):
        for prof in self.professors:
            if prof.get_name() == prof_name:
                return prof
        return None


class Professor:
    def __init__(self, name, courses):
        self.name = name
        self.courses = courses  # List of Course objects

    def get_name(self):
        return self.name

    def get_courses(self):
        return [course.get_name() for course in self.courses]


class Course:
    def __init__(self, name, students):
        self.name = name
        self.students = students  # List of Student objects

    def get_name(self):
        return self.name

    def get_students(self):
        return [student.get_name() for student in self.students]


class Student:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

# [
#     ['University', 'get_departments()', 'Department'],
#     ['University', 'find_professor()', 'Department'],
#     ['Department', 'find_professor()', 'Professor'],
#     ['Professor', 'get_courses()', 'Course'],
#     ['Course', 'get_students()', 'Student']
# ]
