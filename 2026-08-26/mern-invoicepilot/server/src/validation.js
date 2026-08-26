export const validEmail = value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || '');

export function invoiceTotal(items) {
  if (!Array.isArray(items) || items.length === 0) throw new Error('At least one line item is required');
  const total = items.reduce((sum, item) => {
    const quantity = Number(item.quantity), rate = Number(item.rate);
    if (!String(item.description || '').trim() || !Number.isFinite(quantity) || quantity <= 0 || !Number.isFinite(rate) || rate < 0) throw new Error('Every item needs a description, positive quantity, and non-negative rate');
    return sum + quantity * rate;
  }, 0);
  return Math.round((total + Number.EPSILON) * 100) / 100;
}

export function requiredStrings(body, names) {
  return names.filter(name => !String(body[name] || '').trim());
}

