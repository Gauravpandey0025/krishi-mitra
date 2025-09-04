export async function loadComponent(selector) {
  const element = document.querySelector(selector);
  if (!element) return;
  
  const source = element.dataset.source;
  if (!source) return;
  
  try {
    const baseUrl = window.location.origin + '/api/preview-68b953862f14244be4c58c2e/';
    const response = await fetch(baseUrl + source);
    const html = await response.text();
    element.innerHTML = html;
  } catch (error) {
    console.error(`Failed to load component ${source}:`, error);
  }
}