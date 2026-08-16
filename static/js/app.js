/**
 * TaskMaster Pro - Frontend JavaScript Application
 * Vanilla JS interacting with Python Flask REST API
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const taskForm = document.getElementById('task-form');
    const taskTitleInput = document.getElementById('task-title');
    const taskDescInput = document.getElementById('task-desc');
    const taskListContainer = document.getElementById('task-list');
    const loadingSpinner = document.getElementById('loading-spinner');
    const emptyState = document.getElementById('empty-state');
    const emptyStateText = document.getElementById('empty-state-text');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');

    // Stats Elements
    const statTotal = document.getElementById('stat-total');
    const statPending = document.getElementById('stat-pending');
    const statCompleted = document.getElementById('stat-completed');
    const countAll = document.getElementById('count-all');
    const countPending = document.getElementById('count-pending');
    const countCompleted = document.getElementById('count-completed');

    // Filter Buttons
    const filterBtns = document.querySelectorAll('.filter-btn');

    // Edit Modal Elements
    const editModal = document.getElementById('edit-modal');
    const editTaskForm = document.getElementById('edit-task-form');
    const editTaskId = document.getElementById('edit-task-id');
    const editTaskTitle = document.getElementById('edit-task-title');
    const editTaskDesc = document.getElementById('edit-task-desc');
    const editTaskCompleted = document.getElementById('edit-task-completed');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelModalBtn = document.getElementById('cancel-modal-btn');

    // State Variables
    let tasks = [];
    let currentFilter = 'all';

    // Initialize Application
    init();

    async function init() {
        setupEventListeners();
        await checkHealth();
        await fetchTasks();
        // Periodically check health status every 30 seconds
        setInterval(checkHealth, 30000);
    }

    function setupEventListeners() {
        // Form Submit
        taskForm.addEventListener('submit', handleAddTask);
        editTaskForm.addEventListener('submit', handleSaveEdit);

        // Filter Switchers
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                renderTasks();
            });
        });

        // Modal Close Listeners
        closeModalBtn.addEventListener('click', closeModal);
        cancelModalBtn.addEventListener('click', closeModal);
        editModal.addEventListener('click', (e) => {
            if (e.target === editModal) closeModal();
        });
    }

    // -------------------------------------------------------------------
    // API Communication Methods
    // -------------------------------------------------------------------

    async function checkHealth() {
        try {
            const response = await fetch('/health');
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'healthy') {
                    statusIndicator.className = 'status-indicator online';
                    statusText.textContent = 'System Healthy';
                } else {
                    statusIndicator.className = 'status-indicator offline';
                    statusText.textContent = 'Degraded DB';
                }
            } else {
                statusIndicator.className = 'status-indicator offline';
                statusText.textContent = 'Service Unavailable';
            }
        } catch (error) {
            statusIndicator.className = 'status-indicator offline';
            statusText.textContent = 'Backend Offline';
        }
    }

    async function fetchTasks() {
        showLoading(true);
        try {
            const response = await fetch('/api/tasks');
            if (!response.ok) throw new Error('Failed to fetch tasks');
            tasks = await response.json();
            updateStats();
            renderTasks();
        } catch (error) {
            console.error('Error loading tasks:', error);
            showToast('Failed to load tasks from server', 'danger');
        } finally {
            showLoading(false);
        }
    }

    async function handleAddTask(e) {
        e.preventDefault();
        const title = taskTitleInput.value.trim();
        const description = taskDescInput.value.trim();

        if (!title) {
            showToast('Please enter a task title', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description }),
            });

            if (!response.ok) throw new Error('Failed to create task');

            const newTask = await response.json();
            tasks.unshift(newTask);
            taskForm.reset();
            updateStats();
            renderTasks();
            showToast('Task created successfully!', 'success');
        } catch (error) {
            console.error('Error adding task:', error);
            showToast('Failed to create task', 'danger');
        }
    }

    async function toggleTaskStatus(id, currentStatus) {
        const endpoint = currentStatus ? `/api/tasks/${id}/pending` : `/api/tasks/${id}/complete`;
        try {
            const response = await fetch(endpoint, { method: 'PATCH' });
            if (!response.ok) throw new Error('Failed to update task status');

            const updatedTask = await response.json();
            const index = tasks.findIndex(t => t.id === id);
            if (index !== -1) {
                tasks[index] = updatedTask;
            }
            updateStats();
            renderTasks();
            const actionText = updatedTask.completed ? 'marked as completed' : 'marked as pending';
            showToast(`Task ${actionText}!`, 'success');
        } catch (error) {
            console.error('Error toggling status:', error);
            showToast('Failed to update task status', 'danger');
        }
    }

    async function deleteTask(id) {
        if (!confirm('Are you sure you want to delete this task?')) return;

        try {
            const response = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to delete task');

            tasks = tasks.filter(t => t.id !== id);
            updateStats();
            renderTasks();
            showToast('Task deleted successfully', 'warning');
        } catch (error) {
            console.error('Error deleting task:', error);
            showToast('Failed to delete task', 'danger');
        }
    }

    function openEditModal(task) {
        editTaskId.value = task.id;
        editTaskTitle.value = task.title;
        editTaskDesc.value = task.description || '';
        editTaskCompleted.checked = task.completed;
        editModal.classList.remove('hidden');
    }

    function closeModal() {
        editModal.classList.add('hidden');
        editTaskForm.reset();
    }

    async function handleSaveEdit(e) {
        e.preventDefault();
        const id = parseInt(editTaskId.value);
        const title = editTaskTitle.value.trim();
        const description = editTaskDesc.value.trim();
        const completed = editTaskCompleted.checked;

        if (!title) {
            showToast('Title cannot be empty', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, completed }),
            });

            if (!response.ok) throw new Error('Failed to update task');

            const updatedTask = await response.json();
            const index = tasks.findIndex(t => t.id === id);
            if (index !== -1) {
                tasks[index] = updatedTask;
            }

            closeModal();
            updateStats();
            renderTasks();
            showToast('Task updated successfully!', 'success');
        } catch (error) {
            console.error('Error saving task:', error);
            showToast('Failed to save changes', 'danger');
        }
    }

    // -------------------------------------------------------------------
    // UI Rendering & Helpers
    // -------------------------------------------------------------------

    function updateStats() {
        const total = tasks.length;
        const completed = tasks.filter(t => t.completed).length;
        const pending = total - completed;

        statTotal.textContent = total;
        statPending.textContent = pending;
        statCompleted.textContent = completed;

        countAll.textContent = total;
        countPending.textContent = pending;
        countCompleted.textContent = completed;
    }

    function renderTasks() {
        const filteredTasks = tasks.filter(task => {
            if (currentFilter === 'pending') return !task.completed;
            if (currentFilter === 'completed') return task.completed;
            return true;
        });

        taskListContainer.innerHTML = '';

        if (filteredTasks.length === 0) {
            emptyState.classList.remove('hidden');
            if (currentFilter === 'pending') {
                emptyStateText.textContent = 'No pending tasks remaining!';
            } else if (currentFilter === 'completed') {
                emptyStateText.textContent = 'No completed tasks yet.';
            } else {
                emptyStateText.textContent = 'Your task list is empty! Create your first task above.';
            }
            return;
        }

        emptyState.classList.add('hidden');

        filteredTasks.forEach(task => {
            const card = document.createElement('div');
            card.className = `task-item ${task.completed ? 'completed-item' : 'pending-item'}`;
            
            const formattedDate = formatDate(task.created_at);

            card.innerHTML = `
                <div class="task-main">
                    <div class="task-meta">
                        <span class="task-badge ${task.completed ? 'completed' : 'pending'}">
                            ${task.completed ? '<i class="fa-solid fa-check"></i> Completed' : '<i class="fa-solid fa-clock"></i> Pending'}
                        </span>
                        <span class="task-date"><i class="fa-regular fa-calendar-alt"></i> ${formattedDate}</span>
                    </div>
                    <h3 class="task-title">${escapeHTML(task.title)}</h3>
                    ${task.description ? `<p class="task-desc">${escapeHTML(task.description)}</p>` : ''}
                </div>
                <div class="task-actions">
                    <button class="action-btn ${task.completed ? 'pending-btn' : 'complete-btn'}" 
                            title="${task.completed ? 'Mark as Pending' : 'Mark as Completed'}"
                            data-action="toggle">
                        <i class="fa-solid ${task.completed ? 'fa-arrow-rotate-left' : 'fa-check'}"></i>
                    </button>
                    <button class="action-btn edit-btn" title="Edit Task" data-action="edit">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="action-btn delete-btn" title="Delete Task" data-action="delete">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            `;

            // Action Button Event Handlers
            card.querySelector('[data-action="toggle"]').addEventListener('click', () => toggleTaskStatus(task.id, task.completed));
            card.querySelector('[data-action="edit"]').addEventListener('click', () => openEditModal(task));
            card.querySelector('[data-action="delete"]').addEventListener('click', () => deleteTask(task.id));

            taskListContainer.appendChild(card);
        });
    }

    function showLoading(show) {
        if (show) {
            loadingSpinner.classList.remove('hidden');
            taskListContainer.classList.add('hidden');
        } else {
            loadingSpinner.classList.add('hidden');
            taskListContainer.classList.remove('hidden');
        }
    }

    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let iconClass = 'fa-info-circle';
        if (type === 'success') iconClass = 'fa-circle-check';
        if (type === 'danger') iconClass = 'fa-circle-xmark';
        if (type === 'warning') iconClass = 'fa-triangle-exclamation';

        toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> <span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    function escapeHTML(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        try {
            const date = new Date(dateStr);
            if (isNaN(date)) return dateStr;
            return date.toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        } catch (e) {
            return dateStr;
        }
    }
});
