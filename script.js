// NEXO - Periódico Digital Financiero
// JavaScript para funcionalidad del sitio web

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todas las funcionalidades
    initSmoothScrolling();
    initNewsletterForm();
    initMarketData();
    initAnimations();
    initMobileMenu();
});

// Smooth scrolling para navegación
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Funcionalidad del formulario de newsletter
function initNewsletterForm() {
    const form = document.getElementById('subscriptionForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const name = document.getElementById('name').value;
            
            // Validación básica
            if (!isValidEmail(email)) {
                showNotification('Por favor, ingresa un email válido', 'error');
                return;
            }
            
            if (name.trim().length < 2) {
                showNotification('Por favor, ingresa tu nombre completo', 'error');
                return;
            }
            
            // Simular envío del formulario
            submitNewsletterSubscription(email, name);
        });
    }
}

// Validación de email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Envío de suscripción al newsletter
function submitNewsletterSubscription(email, name) {
    const submitButton = document.querySelector('.subscription-form button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Mostrar estado de carga
    submitButton.textContent = 'Suscribiendo...';
    submitButton.disabled = true;
    
    // Simular llamada a API (reemplazar con endpoint real)
    setTimeout(() => {
        // Aquí iría la llamada real a tu servicio de newsletter
        // Por ejemplo: Mailchimp, ConvertKit, etc.
        
        try {
            // Simulación de éxito
            showNotification(`¡Gracias ${name}! Te has suscrito exitosamente al newsletter NEXO.`, 'success');
            
            // Limpiar formulario
            document.getElementById('subscriptionForm').reset();
            
            // Tracking de conversión (opcional)
            trackNewsletterSubscription(email, name);
            
        } catch (error) {
            showNotification('Hubo un error al procesar tu suscripción. Por favor, intenta nuevamente.', 'error');
        } finally {
            // Restaurar botón
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }, 2000);
}

// Sistema de notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Estilos para la notificación
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#38a169' : type === 'error' ? '#e53e3e' : '#3182ce'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        max-width: 400px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Funcionalidad de cerrar
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        removeNotification(notification);
    });
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        removeNotification(notification);
    }, 5000);
}

function removeNotification(notification) {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Datos de mercado en tiempo real (simulado)
function initMarketData() {
    const marketCards = document.querySelectorAll('.market-card');
    
    // Simular actualizaciones de mercado cada 30 segundos
    setInterval(() => {
        updateMarketData();
    }, 30000);
    
    // Actualización inicial
    updateMarketData();
}

function updateMarketData() {
    const markets = [
        { name: 'S&P 500', basePrice: 4567.89 },
        { name: 'NASDAQ', basePrice: 14234.56 },
        { name: 'DOW JONES', basePrice: 34567.12 },
        { name: 'EUR/USD', basePrice: 1.0876 }
    ];
    
    const marketCards = document.querySelectorAll('.market-card');
    
    marketCards.forEach((card, index) => {
        if (markets[index]) {
            const market = markets[index];
            const priceElement = card.querySelector('.market-price');
            const changeElement = card.querySelector('.market-change');
            
            // Simular cambio de precio (±2%)
            const changePercent = (Math.random() - 0.5) * 4;
            const newPrice = market.basePrice * (1 + changePercent / 100);
            
            // Actualizar precio
            if (market.name === 'EUR/USD') {
                priceElement.textContent = newPrice.toFixed(4);
            } else {
                priceElement.textContent = newPrice.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
            
            // Actualizar cambio
            const changeText = `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
            changeElement.textContent = changeText;
            changeElement.className = `market-change ${changePercent >= 0 ? 'positive' : 'negative'}`;
            
            // Animación de actualización
            card.style.transform = 'scale(1.02)';
            setTimeout(() => {
                card.style.transform = 'scale(1)';
            }, 200);
        }
    });
}

// Animaciones al hacer scroll
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observar elementos para animación
    const animatedElements = document.querySelectorAll('.market-card, .analysis-card, .newsletter-form');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Menú móvil (si se implementa en el futuro)
function initMobileMenu() {
    // Placeholder para funcionalidad de menú móvil
    // Se puede expandir según necesidades
}

// Tracking de eventos (opcional - para analytics)
function trackNewsletterSubscription(email, name) {
    // Aquí puedes integrar con Google Analytics, Facebook Pixel, etc.
    if (typeof gtag !== 'undefined') {
        gtag('event', 'newsletter_subscription', {
            'event_category': 'engagement',
            'event_label': 'newsletter',
            'value': 1
        });
    }
    
    console.log('Newsletter subscription tracked:', { email, name });
}

// Utilidades adicionales
const Utils = {
    // Formatear números
    formatNumber: (num) => {
        return new Intl.NumberFormat('es-ES').format(num);
    },
    
    // Formatear fechas
    formatDate: (date) => {
        return new Intl.DateTimeFormat('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(date);
    },
    
    // Debounce para optimizar eventos
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Agregar estilos CSS para animaciones
const animationStyles = `
    .animate-in {
        animation: slideInUp 0.6s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification-close:hover {
        opacity: 0.8;
    }
`;

// Inyectar estilos de animación
const styleSheet = document.createElement('style');
styleSheet.textContent = animationStyles;
document.head.appendChild(styleSheet);

// Exportar funciones para uso global si es necesario
window.NEXO = {
    showNotification,
    Utils
};