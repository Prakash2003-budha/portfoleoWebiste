// schema.js
// Loads metadata from the backend so the frontend can render the portfolio
// sections dynamically instead of relying on a hardcoded local schema.

let PORTFOLIO_SCHEMA = null;

async function loadPortfolioSchema() {
  if (!PORTFOLIO_SCHEMA) {
    PORTFOLIO_SCHEMA = await api.get('/portfolio/schema');
  }
  return PORTFOLIO_SCHEMA;
}

function getSectionConfig(section) {
  return PORTFOLIO_SCHEMA ? PORTFOLIO_SCHEMA[section] : null;
}

function getPortfolioSchema() {
  return PORTFOLIO_SCHEMA;
}

window.loadPortfolioSchema = loadPortfolioSchema;
window.getSectionConfig = getSectionConfig;
window.getPortfolioSchema = getPortfolioSchema;
window.PORTFOLIO_SCHEMA = PORTFOLIO_SCHEMA;
