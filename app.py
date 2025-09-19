import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="WorkLab",
    page_icon="[W]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .todo-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #ffffff;
        color: #333333;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .todo-card h4 {
        color: #2c3e50;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .todo-card p {
        color: #555555;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .todo-card small {
        color: #666666;
        font-size: 12px;
    }
    .priority-urgent { 
        border-left: 5px solid #ff4444;
        background-color: #fff5f5;
    }
    .priority-high { 
        border-left: 5px solid #ff8800;
        background-color: #fffaf0;
    }
    .priority-medium { 
        border-left: 5px solid #ffaa00;
        background-color: #fffef0;
    }
    .priority-low { 
        border-left: 5px solid #00aa00;
        background-color: #f0fff0;
    }
    .status-completed { 
        opacity: 0.6; 
        text-decoration: line-through;
        background-color: #f8f9fa;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .overdue-text {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Dark mode compatibility */
    @media (prefers-color-scheme: dark) {
        .todo-card {
            background-color: #2b2b2b;
            color: #e0e0e0;
            border-color: #444444;
        }
        .todo-card h4 {
            color: #ffffff;
        }
        .todo-card p {
            color: #cccccc;
        }
        .todo-card small {
            color: #aaaaaa;
        }
        .priority-urgent { 
            background-color: #3d1a1a;
        }
        .priority-high { 
            background-color: #3d2a0f;
        }
        .priority-medium { 
            background-color: #3d3d0f;
        }
        .priority-low { 
            background-color: #0f3d0f;
        }
        .status-completed { 
            background-color: #333333;
        }
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def make_api_request(method: str, endpoint: str, data=None, params=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        elif method.upper() == "PATCH":
            response = requests.patch(url, params=params)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure FastAPI server is running on port 8000")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def format_priority_icon(priority: str) -> str:
    """Return icon for priority level"""
    icons = {
        "urgent": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    return icons.get(priority, "🟢")

def format_status_icon(status: str) -> str:
    """Return icon for status"""
    icons = {
        "pending": "⏳",
        "in_progress": "▶️",
        "completed": "✅",
        "cancelled": "❌"
    }
    return icons.get(status, "⏳")

def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    if not date_str:
        return "Not set"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def is_overdue(due_date_str: str, status: str) -> bool:
    """Check if todo is overdue"""
    if not due_date_str or status == "completed":
        return False
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return due_date < datetime.now()
    except:
        return False

# Main app functions
def display_todo_card(todo: Dict):
    """Display a todo item as a card"""
    priority_class = f"priority-{todo['priority']}"
    status_class = "status-completed" if todo['status'] == 'completed' else ""
    
    overdue = is_overdue(todo['due_date'], todo['status'])
    overdue_text = '<span class="overdue-text"> [OVERDUE]</span>' if overdue else ""
    
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="todo-card {priority_class} {status_class}">
                <h4>{format_priority_icon(todo['priority'])} {todo['title']}{overdue_text}</h4>
                <p>{todo['description'] or 'No description provided'}</p>
                <small>
                    📅 Due: {format_date(todo['due_date'])} | 
                    📁 Category: {todo['category'] or 'Uncategorized'} |
                    ⏱️ Est: {todo['estimated_hours'] or 'N/A'}h
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.write(f"{format_status_icon(todo['status'])} {todo['status'].replace('_', ' ').title()}")
        
        with col3:
            new_status = st.selectbox(
                "Change Status",
                ["pending", "in_progress", "completed", "cancelled"],
                index=["pending", "in_progress", "completed", "cancelled"].index(todo['status']),
                key=f"status_{todo['id']}"
            )
            if new_status != todo['status']:
                if make_api_request("PATCH", f"/todos/{todo['id']}/status", params={"status": new_status}):
                    st.success(f"Status updated to {new_status.replace('_', ' ').title()}!")
                    st.rerun()
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{todo['id']}", help="Delete this task"):
                if st.session_state.get(f"confirm_delete_{todo['id']}", False):
                    if make_api_request("DELETE", f"/todos/{todo['id']}"):
                        st.success("Task deleted successfully!")
                        st.rerun()
                else:
                    st.session_state[f"confirm_delete_{todo['id']}"] = True
                    st.warning("Click again to confirm deletion")

def create_todo_form():
    """Create new todo form"""
    st.subheader("🆕 Create New Task")
    
    with st.form("create_todo"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title *", placeholder="Enter a clear, actionable task title")
            description = st.text_area("Description", placeholder="Add details, context, or notes for this task")
            category = st.text_input("Category", placeholder="e.g., Work, Personal, Health, Learning")
            
        with col2:
            priority = st.selectbox("Priority Level", ["low", "medium", "high", "urgent"], index=1)
            due_date = st.date_input("Due Date", value=None, help="When should this task be completed?")
            estimated_hours = st.number_input("Estimated Hours", min_value=0, step=1, help="How long will this take?")
            is_recurring = st.checkbox("Recurring Task", help="Does this task repeat?")
            
        if is_recurring:
            recurrence_pattern = st.selectbox("Recurrence Pattern", ["daily", "weekly", "monthly"])
        else:
            recurrence_pattern = None
        
        tags = st.text_input("Tags", placeholder="Comma-separated tags (e.g., urgent, meeting, review)")
        
        submitted = st.form_submit_button("✨ Create Task", type="primary", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("⚠️ Task title is required!")
                return
            
            todo_data = {
                "title": title,
                "description": description,
                "priority": priority,
                "category": category,
                "estimated_hours": estimated_hours if estimated_hours > 0 else None,
                "is_recurring": is_recurring,
                "recurrence_pattern": recurrence_pattern,
                "tags": tags if tags else None,
                "due_date": due_date.isoformat() + "T00:00:00" if due_date else None
            }
            
            result = make_api_request("POST", "/todos/", data=todo_data)
            if result:
                st.success("🎉 Task created successfully!")
                st.session_state.page = "All Tasks"
                st.rerun()

def display_dashboard():
    """Display dashboard with statistics"""
    st.subheader("📊 Dashboard Overview")
    
    if st.button("➕ Add New Task", type="primary", use_container_width=True):
        st.session_state.page = "Create Task"
        st.rerun()
    
    stats = make_api_request("GET", "/todos/stats/summary")
    if not stats:
        st.warning("Unable to load dashboard statistics. Please check your API connection.")
        return
    
    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total Tasks", stats['total'])
    with col2:
        st.metric("⏳ Pending", stats['status']['pending'])
    with col3:
        st.metric("▶️ In Progress", stats['status']['in_progress'])
    with col4:
        st.metric("✅ Completed", stats['status']['completed'])
    with col5:
        st.metric("📈 Completion Rate", f"{stats['completion_rate']}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        status_data = stats['status']
        fig_status = px.pie(
            values=list(status_data.values()),
            names=list(status_data.keys()),
            title="📊 Task Status Distribution",
            color_discrete_map={
                'pending': '#ffd700',
                'in_progress': '#4169e1',
                'completed': '#32cd32',
                'cancelled': '#ff6347'
            }
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        priority_data = stats['priority']
        fig_priority = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="🎯 Task Priority Distribution",
            color=list(priority_data.keys()),
            color_discrete_map={
                'urgent': '#ff4444',
                'high': '#ff8800',
                'medium': '#ffaa00',
                'low': '#00aa00'
            }
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    if stats.get('overdue', 0) > 0:
        st.error(f"⚠️ You have {stats['overdue']} overdue tasks that need attention!")
        overdue_todos = make_api_request("GET", "/todos/overdue/")
        if overdue_todos:
            st.write("**🔥 Overdue Tasks:**")
            for todo in overdue_todos[:5]:
                st.write(f"• **{todo['title']}** - Due: {format_date(todo['due_date'])}")
    
    st.subheader("📅 Due Today")
    due_today = make_api_request("GET", "/todos/due-today/")
    if due_today:
        for todo in due_today:
            display_todo_card(todo)
    else:
        st.info("🎉 No tasks due today! You're all caught up.")

def main():
    """Main application"""
    st.title("🚀 WorkLab")
    st.markdown("**Your intelligent task management workspace**")
    st.markdown("Organize, prioritize, and track your work with powerful analytics and insights")
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Sidebar
    with st.sidebar:
        st.header("🧭 Navigation")
        st.session_state.page = st.radio(
            "Go to",
            ["Dashboard", "All Tasks", "Create Task", "Analytics"],
            index=["Dashboard", "All Tasks", "Create Task", "Analytics"].index(st.session_state.page)
        )
        
        st.header("🔍 Filters")
        status_filter = st.selectbox(
            "Filter by Status", 
            ["all", "pending", "in_progress", "completed", "cancelled"],
            format_func=lambda x: f"All Statuses" if x == "all" else x.replace('_', ' ').title()
        )
        priority_filter = st.selectbox(
            "Filter by Priority", 
            ["all", "urgent", "high", "medium", "low"],
            format_func=lambda x: f"All Priorities" if x == "all" else x.title()
        )
        search_query = st.text_input("🔍 Search Tasks", placeholder="Search in title or description...")
        
        st.header("📈 Quick Stats")
        stats = make_api_request("GET", "/todos/stats/summary")
        if stats:
            st.metric("Total", stats['total'])
            st.metric("Pending", stats['status']['pending'])
            st.metric("Overdue", stats.get('overdue', 0))
    
    # Main content area
    if st.session_state.page == "Dashboard":
        display_dashboard()
    
    elif st.session_state.page == "All Tasks":
        st.subheader("📋 All Tasks")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Manage and organize all your tasks in one place")
        with col2:
            if st.button("➕ Add New Task", type="primary"):
                st.session_state.page = "Create Task"
                st.rerun()
        
        params = {}
        if status_filter != "all":
            params["status"] = status_filter
        if priority_filter != "all":
            params["priority"] = priority_filter
        if search_query:
            params["search"] = search_query
        
        todos = make_api_request("GET", "/todos/", params=params)
        
        if todos:
            st.write(f"📊 Found **{len(todos)} tasks** matching your criteria")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                sort_by = st.selectbox(
                    "Sort by", 
                    ["created_at", "due_date", "priority", "status"],
                    format_func=lambda x: {
                        "created_at": "📅 Creation Date",
                        "due_date": "⏰ Due Date", 
                        "priority": "🎯 Priority",
                        "status": "📊 Status"
                    }.get(x, x)
                )
            
            if sort_by == "priority":
                priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
                todos.sort(key=lambda x: priority_order.get(x['priority'], 4))
            elif sort_by == "due_date":
                todos.sort(key=lambda x: x['due_date'] or "9999-12-31")
            
            st.markdown("---")
            for todo in todos:
                display_todo_card(todo)
        else:
            st.info("📭 No tasks found matching your criteria. Try adjusting your filters or create a new task!")
    
    elif st.session_state.page == "Create Task":
        create_todo_form()
    
    elif st.session_state.page == "Analytics":
        st.subheader("📊 Analytics & Insights")
        
        stats = make_api_request("GET", "/todos/stats/summary")
        if not stats:
            st.warning("Unable to load analytics data. Please check your API connection.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📝 Total Tasks Created", stats['total'])
            st.metric("✅ Tasks Completed", stats['status']['completed'])
            st.metric("❌ Tasks Cancelled", stats['status']['cancelled'])
        
        with col2:
            completion_rate = stats.get('completion_rate', 0)
            st.metric("🎯 Success Rate", f"{completion_rate}%")
            active_tasks = stats['status']['pending'] + stats['status']['in_progress']
            st.metric("⚡ Active Tasks", active_tasks)
            st.metric("🔥 Overdue Tasks", stats.get('overdue', 0))
        
        categories = make_api_request("GET", "/todos/categories/")
        if categories:
            st.subheader("📁 Task Categories")
            category_cols = st.columns(min(3, len(categories)))
            for i, category in enumerate(categories):
                with category_cols[i % 3]:
                    st.info(f"📂 {category}")
        
        st.subheader("📈 Progress Trends")
        st.info("💡 Progress tracking over time will be available as you create more tasks and build your work history.")

if __name__ == "__main__":
    main()