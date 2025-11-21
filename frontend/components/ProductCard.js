export default function ProductCard({ product }) {
  const fallback =
    'data:image/svg+xml;utf8,' +
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">' +
    '<rect width="100%" height="100%" fill="%23f3f4f6"/>' +
    '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23888" font-family="Arial,sans-serif" font-size="20">No image</text>' +
    '</svg>';

  const formatNumber = (v) => {
    if (typeof v === 'number') return v.toFixed(2);
    if (v == null) return null;
    const asNum = parseFloat(String(v).replace(/[^0-9.,-]/g, '').replace(',', '.'));
    return Number.isFinite(asNum) ? asNum.toFixed(2) : null;
  };

  const extractFirstNumber = (text) => {
    if (text == null) return null;
    const m = String(text).match(/[0-9]+[.,]?[0-9]*/);
    if (!m) return null;
    const n = m[0].replace(',', '.');
    const v = parseFloat(n);
    return Number.isFinite(v) ? v.toFixed(2) : null;
  };

  const normalizeImageUrl = (u) => {
    if (!u) return u;
    try {
      const s = String(u);
      if (s.includes('cloudinary.com') && s.includes('/upload/')) {
        return s
          .replace(/q_\d+/g, 'q_auto')
          .replace(/w_\d+/g, 'w_512')
          .replace(/h_\d+/g, 'h_512');
      }
      return s;
    } catch (e) {
      return u;
    }
  };

  
  let primaryPrice = null;
  const candidates = [
    product?.price,
    product?.shelf_price,
    product?.shelfPrice,
    product?.shelfPriceRaw,
    product?.price_raw,
    product?.price_text,
    product?.priceString,
    product?.priceStringRaw,
  ];

  for (const c of candidates) {
    const f = formatNumber(c) ?? extractFirstNumber(c);
    if (f) {
      primaryPrice = f;
      break;
    }
  }

  let perKgLabel = null;
  if (product?.price_per_kg != null) {
    perKgLabel = formatNumber(product.price_per_kg) ?? String(product.price_per_kg);
    if (perKgLabel && !String(perKgLabel).includes('€')) perKgLabel = `${perKgLabel} € / kg`;
  } else {
    const unit = String(product?.unit || product?.size || '').toLowerCase();
    if (/kg/.test(unit) && product?.price != null) {
      const p = formatNumber(product.price);
      if (p) perKgLabel = `${p} € / kg`;
    } else if (typeof product?.price === 'string' && /\/kg|per kg|per-kg|kg/i.test(product.price)) {
      perKgLabel = product.price;
    }
  }

  return (
    <div className="w-64 p-4 border rounded-lg shadow-sm hover:shadow-md transition flex flex-col justify-between bg-white">
      <div className="h-36 mb-3 bg-gray-100 rounded-md overflow-hidden flex items-center justify-center">
        <img
          src={normalizeImageUrl(product?.image) || fallback}
          alt={product?.name || 'product image'}
          loading="lazy"
          className="h-full w-full object-cover"
          onError={(e) => {
            if (e?.currentTarget?.src !== fallback) e.currentTarget.src = fallback;
          }}
        />
      </div>

      <div className="flex-1">
        <h3 className="font-semibold text-lg mb-1 h-12 overflow-hidden">{product?.name}</h3>
        <p className="text-sm text-gray-500 mb-2 h-5 overflow-hidden">{product?.store}</p>
      </div>

      <div className="mt-3">
        <p className="font-bold text-lg">{String(primaryPrice).includes('€') ? primaryPrice : `${primaryPrice} €`}</p>
        {perKgLabel && <p className="text-sm text-gray-500">{perKgLabel}</p>}
      </div>
    </div>
  );
}
