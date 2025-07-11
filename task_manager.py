#!/usr/bin/env python3
"""
Personal Task Manager - Console Application
A comprehensive task management system with categories, priorities, and persistence.
"""

import json
import os
import datetime
from enum import Enum
from typing import List, Dict, Optional

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class Status(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Task:
    def __init__(self, title: str, description: str = "", category: str = "General", 
                 priority: Priority = Priority.MEDIUM, due_date: str = None):
        self.id = None  # Will be set by TaskManager
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.status = Status.PENDING
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.due_date = self._parse_date(due_date) if due_date else None
        self.completed_at = None
    
    def _parse_date(self, date_str: str) -> Optional[datetime.datetime]:
        """Parse date string in format YYYY-MM-DD or DD/MM/YYYY"""
        try:
            if '-' in date_str:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d")
            elif '/' in date_str:
                return datetime.datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            pass
        return None
    
    def update_status(self, new_status: Status):
        """Update task status and timestamp"""
        self.status = new_status
        self.updated_at = datetime.datetime.now()
        if new_status == Status.COMPLETED:
            self.completed_at = datetime.datetime.now()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and self.status != Status.COMPLETED:
            return datetime.datetime.now() > self.due_date
        return False
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary"""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category', 'General'),
            priority=Priority(data.get('priority', Priority.MEDIUM.value))
        )
        task.id = data.get('id')
        task.status = Status(data.get('status', Status.PENDING.value))
        task.created_at = datetime.datetime.fromisoformat(data['created_at'])
        task.updated_at = datetime.datetime.fromisoformat(data['updated_at'])
        if data.get('due_date'):
            task.due_date = datetime.datetime.fromisoformat(data['due_date'])
        if data.get('completed_at'):
            task.completed_at = datetime.datetime.fromisoformat(data['completed_at'])
        return task
    
    def __str__(self) -> str:
        """String representation of task"""
        due_str = f" (Due: {self.due_date.strftime('%Y-%m-%d')})" if self.due_date else ""
        overdue_str = " [OVERDUE]" if self.is_overdue() else ""
        return f"[{self.id}] {self.title} - {self.status.value} - {self.priority.value}{due_str}{overdue_str}"

class TaskManager:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.tasks = [Task.from_dict(task_data) for task_data in data['tasks']]
                    self.next_id = data.get('next_id', 1)
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
            self.next_id = 1
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            data = {
                'tasks': [task.to_dict() for task in self.tasks],
                'next_id': self.next_id
            }
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, title: str, description: str = "", category: str = "General", 
                 priority: Priority = Priority.MEDIUM, due_date: str = None) -> Task:
        """Add a new task"""
        task = Task(title, description, category, priority, due_date)
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: int, new_status: Status) -> bool:
        """Update task status"""
        task = self.get_task(task_id)
        if task:
            task.update_status(new_status)
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False
    
    def get_tasks_by_status(self, status: Status) -> List[Task]:
        """Get tasks filtered by status"""
        return [task for task in self.tasks if task.status == status]
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get tasks filtered by category"""
        return [task for task in self.tasks if task.category.lower() == category.lower()]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(task.category for task in self.tasks))
    
    def get_statistics(self) -> Dict:
        """Get task statistics"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == Status.COMPLETED])
        pending = len([t for t in self.tasks if t.status == Status.PENDING])
        in_progress = len([t for t in self.tasks if t.status == Status.IN_PROGRESS])
        overdue = len(self.get_overdue_tasks())
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': overdue,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

class TaskManagerApp:
    def __init__(self):
        self.task_manager = TaskManager()
        self.running = True
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header"""
        print("=" * 60)
        print("          📋 PERSONAL TASK MANAGER 📋")
        print("=" * 60)
    
    def print_menu(self):
        """Print main menu"""
        print("\n🔹 MAIN MENU:")
        print("1. ➕ Add Task")
        print("2. 📋 View All Tasks")
        print("3. 🔍 View Tasks by Status")
        print("4. 📁 View Tasks by Category")
        print("5. ✏️  Update Task Status")
        print("6. 🗑️  Delete Task")
        print("7. ⚠️  View Overdue Tasks")
        print("8. 📊 View Statistics")
        print("9. 🔧 Settings")
        print("0. 🚪 Exit")
        print("-" * 40)
    
    def get_user_input(self, prompt: str, input_type: type = str, required: bool = True):
        """Get validated user input"""
        while True:
            try:
                value = input(prompt).strip()
                if not value and required:
                    print("❌ This field is required. Please try again.")
                    continue
                if not value and not required:
                    return None
                
                if input_type == int:
                    return int(value)
                elif input_type == float:
                    return float(value)
                else:
                    return value
            except ValueError:
                print(f"❌ Please enter a valid {input_type.__name__}.")
    
    def get_priority_choice(self) -> Priority:
        """Get priority choice from user"""
        print("\n🎯 Priority levels:")
        for i, priority in enumerate(Priority, 1):
            print(f"{i}. {priority.value}")
        
        while True:
            choice = self.get_user_input("Select priority (1-4): ", int)
            if 1 <= choice <= 4:
                return list(Priority)[choice - 1]
            print("❌ Invalid choice. Please select 1-4.")
    
    def get_status_choice(self) -> Status:
        """Get status choice from user"""
        print("\n📊 Status options:")
        for i, status in enumerate(Status, 1):
            print(f"{i}. {status.value}")
        
        while True:
            choice = self.get_user_input("Select status (1-4): ", int)
            if 1 <= choice <= 4:
                return list(Status)[choice - 1]
            print("❌ Invalid choice. Please select 1-4.")
    
    def add_task(self):
        """Add a new task"""
        print("\n➕ ADD NEW TASK")
        print("-" * 20)
        
        title = self.get_user_input("📝 Task title: ")
        description = self.get_user_input("📄 Description (optional): ", required=False)
        category = self.get_user_input("📁 Category (optional): ", required=False) or "General"
        priority = self.get_priority_choice()
        due_date = self.get_user_input("📅 Due date (YYYY-MM-DD or DD/MM/YYYY, optional): ", required=False)
        
        try:
            task = self.task_manager.add_task(title, description, category, priority, due_date)
            print(f"✅ Task '{task.title}' added successfully with ID {task.id}!")
        except Exception as e:
            print(f"❌ Error adding task: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_all_tasks(self):
        """View all tasks"""
        print("\n📋 ALL TASKS")
        print("-" * 20)
        
        if not self.task_manager.tasks:
            print("📭 No tasks found.")
        else:
            # Sort tasks by priority and due date
            sorted_tasks = sorted(self.task_manager.tasks, 
                                key=lambda t: (t.priority.value, t.due_date or datetime.datetime.max))
            
            for task in sorted_tasks:
                status_icon = "✅" if task.status == Status.COMPLETED else "🔄" if task.status == Status.IN_PROGRESS else "⏳"
                priority_icon = "🔴" if task.priority == Priority.URGENT else "🟡" if task.priority == Priority.HIGH else "🟢"
                
                print(f"\n{status_icon} {priority_icon} {task}")
                if task.description:
                    print(f"   💬 {task.description}")
                print(f"   📁 Category: {task.category}")
                print(f"   📅 Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        input("\nPress Enter to continue...")
    
    def view_tasks_by_status(self):
        """View tasks filtered by status"""
        print("\n🔍 TASKS BY STATUS")
        print("-" * 20)
        
        status = self.get_status_choice()
        tasks = self.task_manager.get_tasks_by_status(status)
        
        if not tasks:
            print(f"📭 No tasks found with status '{status.value}'.")
        else:
            print(f"\n📊 Tasks with status '{status.value}':")
            for task in tasks:
                print(f"  • {task}")
        
        input("\nPress Enter to continue...")
    
    def view_tasks_by_category(self):
        """View tasks filtered by category"""
        print("\n📁 TASKS BY CATEGORY")
        print("-" * 20)
        
        categories = self.task_manager.get_categories()
        if not categories:
            print("📭 No categories found.")
            input("\nPress Enter to continue...")
            return
        
        print("\n📂 Available categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        choice = self.get_user_input("Select category number: ", int)
        if 1 <= choice <= len(categories):
            selected_category = categories[choice - 1]
            tasks = self.task_manager.get_tasks_by_category(selected_category)
            
            print(f"\n📁 Tasks in category '{selected_category}':")
            for task in tasks:
                print(f"  • {task}")
        else:
            print("❌ Invalid category selection.")
        
        input("\nPress Enter to continue...")
    
    def update_task_status(self):
        """Update task status"""
        print("\n✏️ UPDATE TASK STATUS")
        print("-" * 20)
        
        if not self.task_manager.tasks:
            print("📭 No tasks available.")
            input("\nPress Enter to continue...")
            return
        
        # Show available tasks
        print("\n📋 Available tasks:")
        for task in self.task_manager.tasks:
            print(f"  {task}")
        
        task_id = self.get_user_input("\n🔢 Enter task ID to update: ", int)
        task = self.task_manager.get_task(task_id)
        
        if not task:
            print("❌ Task not found.")
        else:
            print(f"\n📝 Current task: {task}")
            print(f"📊 Current status: {task.status.value}")
            
            new_status = self.get_status_choice()
            if self.task_manager.update_task_status(task_id, new_status):
                print(f"✅ Task status updated to '{new_status.value}'!")
            else:
                print("❌ Failed to update task status.")
        
        input("\nPress Enter to continue...")
    
    def delete_task(self):
        """Delete a task"""
        print("\n🗑️ DELETE TASK")
        print("-" * 20)
        
        if not self.task_manager.tasks:
            print("📭 No tasks available.")
            input("\nPress Enter to continue...")
            return
        
        # Show available tasks
        print("\n📋 Available tasks:")
        for task in self.task_manager.tasks:
            print(f"  {task}")
        
        task_id = self.get_user_input("\n🔢 Enter task ID to delete: ", int)
        task = self.task_manager.get_task(task_id)
        
        if not task:
            print("❌ Task not found.")
        else:
            print(f"\n📝 Task to delete: {task}")
            confirm = self.get_user_input("⚠️ Are you sure you want to delete this task? (yes/no): ").lower()
            
            if confirm in ['yes', 'y']:
                if self.task_manager.delete_task(task_id):
                    print("✅ Task deleted successfully!")
                else:
                    print("❌ Failed to delete task.")
            else:
                print("❌ Task deletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def view_overdue_tasks(self):
        """View overdue tasks"""
        print("\n⚠️ OVERDUE TASKS")
        print("-" * 20)
        
        overdue_tasks = self.task_manager.get_overdue_tasks()
        
        if not overdue_tasks:
            print("🎉 No overdue tasks!")
        else:
            print(f"⚠️ You have {len(overdue_tasks)} overdue task(s):")
            for task in overdue_tasks:
                days_overdue = (datetime.datetime.now() - task.due_date).days
                print(f"  🔴 {task} (Overdue by {days_overdue} days)")
        
        input("\nPress Enter to continue...")
    
    def view_statistics(self):
        """View task statistics"""
        print("\n📊 TASK STATISTICS")
        print("-" * 20)
        
        stats = self.task_manager.get_statistics()
        
        print(f"📈 Total Tasks: {stats['total']}")
        print(f"✅ Completed: {stats['completed']}")
        print(f"⏳ Pending: {stats['pending']}")
        print(f"🔄 In Progress: {stats['in_progress']}")
        print(f"⚠️ Overdue: {stats['overdue']}")
        print(f"📊 Completion Rate: {stats['completion_rate']:.1f}%")
        
        # Category breakdown
        categories = self.task_manager.get_categories()
        if categories:
            print(f"\n📁 Tasks by Category:")
            for category in categories:
                count = len(self.task_manager.get_tasks_by_category(category))
                print(f"  • {category}: {count}")
        
        input("\nPress Enter to continue...")
    
    def settings_menu(self):
        """Settings menu"""
        print("\n🔧 SETTINGS")
        print("-" * 20)
        print("1. 📄 Export Tasks to JSON")
        print("2. 🔄 Backup Tasks")
        print("3. 🧹 Clear Completed Tasks")
        print("4. 📊 Reset All Tasks")
        print("0. ⬅️ Back to Main Menu")
        
        choice = self.get_user_input("\nSelect option: ", int)
        
        if choice == 1:
            self.export_tasks()
        elif choice == 2:
            self.backup_tasks()
        elif choice == 3:
            self.clear_completed_tasks()
        elif choice == 4:
            self.reset_all_tasks()
        elif choice == 0:
            return
        else:
            print("❌ Invalid choice.")
        
        input("\nPress Enter to continue...")
    
    def export_tasks(self):
        """Export tasks to a readable format"""
        filename = f"tasks_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                data = {
                    'exported_at': datetime.datetime.now().isoformat(),
                    'total_tasks': len(self.task_manager.tasks),
                    'tasks': [task.to_dict() for task in self.task_manager.tasks]
                }
                json.dump(data, file, indent=2, ensure_ascii=False)
            print(f"✅ Tasks exported to {filename}")
        except Exception as e:
            print(f"❌ Error exporting tasks: {e}")
    
    def backup_tasks(self):
        """Create a backup of tasks"""
        backup_filename = f"tasks_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import shutil
            shutil.copy2(self.task_manager.filename, backup_filename)
            print(f"✅ Backup created: {backup_filename}")
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
    
    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        completed_tasks = self.task_manager.get_tasks_by_status(Status.COMPLETED)
        if not completed_tasks:
            print("📭 No completed tasks to clear.")
            return
        
        print(f"🧹 Found {len(completed_tasks)} completed tasks.")
        confirm = self.get_user_input("⚠️ Are you sure you want to delete all completed tasks? (yes/no): ").lower()
        
        if confirm in ['yes', 'y']:
            self.task_manager.tasks = [t for t in self.task_manager.tasks if t.status != Status.COMPLETED]
            self.task_manager.save_tasks()
            print("✅ All completed tasks cleared!")
        else:
            print("❌ Operation cancelled.")
    
    def reset_all_tasks(self):
        """Reset all tasks (dangerous operation)"""
        if not self.task_manager.tasks:
            print("📭 No tasks to reset.")
            return
        
        print(f"⚠️ This will delete ALL {len(self.task_manager.tasks)} tasks!")
        confirm = self.get_user_input("⚠️ Are you absolutely sure? Type 'DELETE ALL' to confirm: ")
        
        if confirm == 'DELETE ALL':
            self.task_manager.tasks = []
            self.task_manager.next_id = 1
            self.task_manager.save_tasks()
            print("✅ All tasks have been reset!")
        else:
            print("❌ Operation cancelled.")
    
    def run(self):
        """Main application loop"""
        print("🚀 Welcome to Personal Task Manager!")
        input("Press Enter to start...")
        
        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            try:
                choice = self.get_user_input("🎯 Enter your choice (0-9): ", int)
                
                if choice == 0:
                    self.running = False
                    print("👋 Thank you for using Personal Task Manager!")
                elif choice == 1:
                    self.add_task()
                elif choice == 2:
                    self.view_all_tasks()
                elif choice == 3:
                    self.view_tasks_by_status()
                elif choice == 4:
                    self.view_tasks_by_category()
                elif choice == 5:
                    self.update_task_status()
                elif choice == 6:
                    self.delete_task()
                elif choice == 7:
                    self.view_overdue_tasks()
                elif choice == 8:
                    self.view_statistics()
                elif choice == 9:
                    self.settings_menu()
                else:
                    print("❌ Invalid choice. Please try again.")
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                self.running = False
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                input("\nPress Enter to continue...")

def main():
    """Main function"""
    app = TaskManagerApp()
    app.run()

if __name__ == "__main__":
    main()