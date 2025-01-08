<?php


class Project
{
    private $title;
    private $deadline;
    private $tasks = [];
    private $developers = [];

    public function __construct($title, $deadline)
    {
        $this->title = $title;
        $this->deadline = $deadline;
    }

    public function addTask(Task $task, Developer $developer)
    {
        $this->tasks[] = $task;
        echo "Task '{$task->getName()}' added to project '{$this->title}'.\n";
    }

    public function assignDeveloper(Developer $developer)
    {
        $this->developers[] = $developer;
        echo "Developer '{$developer->getName()}' assigned to project '{$this->title}'.\n";
    }

    public function overview()
    {
        echo "Project '{$this->title}' has " . count($this->tasks) . " tasks and " . count($this->developers) . " developers.\n";
        foreach ($this->tasks as $task) {
            echo " - Task: {$task->getName()} (Assignee: " . ($task->getAssignee() ? $task->getAssignee()->getName() : 'None') . ")\n";
        }
    }
}

class Task
{
    private $name;
    private $description;
    private $assignee = null;
    private $completed = false;

    public function __construct($name, $description)
    {
        $this->name = $name;
        $this->description = $description;
    }

    public function assignTo(Developer $developer)
    {
        $this->assignee = $developer;
        $developer->addTask($this);
        echo "Task '{$this->name}' is assigned to developer '{$developer->getName()}'.\n";
    }

    public function complete()
    {
        if (!$this->completed) {
            $this->completed = true;
            echo "Task '{$this->name}' is now completed.\n";
        } else {
            echo "Task '{$this->name}' was already completed.\n";
        }
    }

    public function getName()
    {
        return $this->name;
    }

    public function getAssignee()
    {
        return $this->assignee;
    }
}

class Developer
{
    private $name;
    private $specialty;
    private $tasks = [];

    public function __construct($name, $specialty)
    {
        $this->name = $name;
        $this->specialty = $specialty;
    }

    public function takeTask(Task $task)
    {
        $this->tasks[] = $task;
        $task->assignTo($this);
        echo "Developer '{$this->name}' took task '{$task->getName()}'.\n";
    }

    public function finishTask(Task $task)
    {
        if (in_array($task, $this->tasks, true)) {
            $task->complete();
        } else {
            echo "Developer '{$this->name}' cannot finish a task not assigned to them.\n";
        }
    }

    public function addTask(Task $task)
    {
        $this->tasks[] = $task;
    }

    public function getName()
    {
        return $this->name;
    }
}

class Manager
{
    private $name;

    public function __construct($name)
    {
        $this->name = $name;
    }

    public function createProject($title, $deadline)
    {
        $project = new Project($title, $deadline);
        echo "Manager '{$this->name}' created project '{$title}'.\n";
        return $project;
    }

    public function hireDeveloper($name, $specialty)
    {
        $dev = new Developer($name, $specialty);
        echo "Manager '{$this->name}' hired developer '{$name}'.\n";
        return $dev;
    }

    public function addTaskToProject(Project $project, Task $task)
    {
        $project->addTask($task);
        echo "Manager '{$this->name}' added task '{$task->getName()}' to project '{$project->getTitle()}'.\n";
    }

    public function assignDevToProject(Project $project, Developer $developer)
    {
        $project->assignDeveloper($developer);
        echo "Manager '{$this->name}' assigned developer '{$developer->getName()}' to project '{$project->getTitle()}'.\n";
    }
}
