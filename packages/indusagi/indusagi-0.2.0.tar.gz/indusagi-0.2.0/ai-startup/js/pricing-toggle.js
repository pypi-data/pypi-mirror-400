// Pricing Toggle Module

function initPricingToggle() {
    const toggle = document.getElementById('pricing-toggle');
    const prices = document.querySelectorAll('.pricing-card__price[data-monthly][data-annual]');
    
    if (!toggle || prices.length === 0) return;

    toggle.addEventListener('change', () => {
        const isAnnual = toggle.checked;
        
        prices.forEach(priceElement => {
            const monthlyPrice = priceElement.getAttribute('data-monthly');
            const annualPrice = priceElement.getAttribute('data-annual');
            
            // Animate price change
            priceElement.style.opacity = '0';
            
            setTimeout(() => {
                if (isAnnual) {
                    priceElement.innerHTML = `$${annualPrice}<span>/month</span>`;
                } else {
                    priceElement.innerHTML = `$${monthlyPrice}<span>/month</span>`;
                }
                priceElement.style.opacity = '1';
            }, 200);
        });
    });
}