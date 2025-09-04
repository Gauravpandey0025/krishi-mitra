// Home page functionality
document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector('[data-id="mobile-menu-toggle"]');
  const mobileNav = document.querySelector('[data-id="mobile-nav"]');
  
  if (mobileMenuToggle && mobileNav) {
    mobileMenuToggle.addEventListener('click', () => {
      mobileNav.classList.toggle('hidden');
      const icon = mobileMenuToggle.querySelector('i');
      if (mobileNav.classList.contains('hidden')) {
        icon.setAttribute('data-lucide', 'menu');
      } else {
        icon.setAttribute('data-lucide', 'x');
      }
      lucide.createIcons();
    });
  }

  // Navigation to different pages
  const getStartedBtn = document.querySelector('[data-id="get-started-btn"]');
  const diseaseDetectionBtn = document.querySelector('[data-id="disease-detection-btn"]');
  const cropRecommendationCard = document.querySelector('[data-id="crop-recommendation-card"]');
  const diseaseDetectionCard = document.querySelector('[data-id="disease-detection-card"]');
  const yieldPredictionCard = document.querySelector('[data-id="yield-prediction-card"]');

  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', () => {
      window.location.href = 'crop-recommendation.html';
    });
  }

  if (diseaseDetectionBtn) {
    diseaseDetectionBtn.addEventListener('click', () => {
      window.location.href = 'disease-detection.html';
    });
  }

  if (cropRecommendationCard) {
    cropRecommendationCard.addEventListener('click', () => {
      window.location.href = 'crop-recommendation.html';
    });
  }

  if (diseaseDetectionCard) {
    diseaseDetectionCard.addEventListener('click', () => {
      window.location.href = 'disease-detection.html';
    });
  }

  if (yieldPredictionCard) {
    yieldPredictionCard.addEventListener('click', () => {
      window.location.href = 'yield-prediction.html';
    });
  }

  // Language selector functionality
  const languageDropdown = document.querySelector('[data-id="language-dropdown"]');
  const mobileLanguageDropdown = document.querySelector('[data-id="mobile-language-dropdown"]');

  function handleLanguageChange(language) {
    // In a real implementation, this would trigger translation
    console.log('Language changed to:', language);
    // Store preference
    localStorage.setItem('preferred-language', language);
  }

  if (languageDropdown) {
    languageDropdown.addEventListener('change', (e) => {
      handleLanguageChange(e.target.value);
    });
  }

  if (mobileLanguageDropdown) {
    mobileLanguageDropdown.addEventListener('change', (e) => {
      handleLanguageChange(e.target.value);
    });
  }

  // Load saved language preference
  const savedLanguage = localStorage.getItem('preferred-language');
  if (savedLanguage) {
    if (languageDropdown) languageDropdown.value = savedLanguage;
    if (mobileLanguageDropdown) mobileLanguageDropdown.value = savedLanguage;
  }
});