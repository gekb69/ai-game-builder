document.addEventListener('DOMContentLoaded', () => {
    // Mock data for dashboard
    const mockData = {
        active_agents: 12,
        active_tasks: 45,
        active_workflows: 8,
        security_level: 'عالي',
        cpu_usage: 65,
        memory_usage: 78,
        disk_usage: 40,
        performance: {
            labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
            data: [65, 59, 80, 81, 56, 55]
        }
    };

    // Update dashboard elements
    document.getElementById('active-agents').textContent = mockData.active_agents;
    document.getElementById('active-tasks').textContent = mockData.active_tasks;
    document.getElementById('active-workflows').textContent = mockData.active_workflows;
    document.getElementById('security-level').textContent = mockData.security_level;

    // Update resource usage
    const cpuProgress = document.getElementById('cpu-usage');
    cpuProgress.style.width = `${mockData.cpu_usage}%`;
    cpuProgress.textContent = `${mockData.cpu_usage}%`;

    const memoryProgress = document.getElementById('memory-usage');
    memoryProgress.style.width = `${mockData.memory_usage}%`;
    memoryProgress.textContent = `${mockData.memory_usage}%`;

    const diskProgress = document.getElementById('disk-usage');
    diskProgress.style.width = `${mockData.disk_usage}%`;
    diskProgress.textContent = `${mockData.disk_usage}%`;

    // Update last update time
    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();

    // Performance Chart
    const ctx = document.getElementById('performanceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: mockData.performance.labels,
            datasets: [{
                label: 'أداء النظام',
                data: mockData.performance.data,
                backgroundColor: 'rgba(74, 144, 226, 0.2)',
                borderColor: 'rgba(74, 144, 226, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
