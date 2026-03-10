// Orbit — Dashboard JS helpers

// Auto-dismiss flash messages after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-flash]').forEach(el => {
    setTimeout(() => el.remove(), 4000);
  });
});

// Relative time formatter
function relativeTime(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'ahora';
  if (diffMin < 60) return `hace ${diffMin}m`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `hace ${diffH}h`;
  return `hace ${Math.floor(diffH / 24)}d`;
}

// Update all relative time elements
function updateRelativeTimes() {
  document.querySelectorAll('[data-time]').forEach(el => {
    el.textContent = relativeTime(el.getAttribute('data-time'));
  });
}
setInterval(updateRelativeTimes, 30000);
updateRelativeTimes();
