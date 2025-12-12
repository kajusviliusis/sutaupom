export default function ProductCard({ product }) {
  const fallback =
    'data:image/svg+xml;utf8,' +
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">' +
    '<rect width="100%" height="100%" fill="%23ffffff"/>' +
    '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23bbb" font-family="Arial,sans-serif" font-size="20">No image</text>' +
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

  const shopRaw = product?.shop || product?.shop_name;
  let shopDisplay = shopRaw;
  if (typeof shopRaw === 'string' && shopRaw.toLowerCase() === 'barbora') {
    shopDisplay = 'Maxima';
  }

  const shopLogoMap = {
    maxima: '/maxima.png',
    iki: '/iki.png',
    rimi: '/rimi.png',
    lidl: '/lidl.png',
    barbora: '/barbora.png',
  };

  const getShopLogoSrc = (name) => {
    if (!name || typeof name !== 'string') return null;
    const key = name.trim().toLowerCase();
    return shopLogoMap[key] || `/${key}.png`;
  };

  const getShopLogoClass = (name) => {
    if (!name || typeof name !== 'string') return 'h-5 w-auto';
    const key = name.trim().toLowerCase();
    // didesnes logo prie iki ir lidl
    if (key === 'iki' || key === 'lidl') return 'h-6 w-auto';
    return 'h-5 w-auto';
  };

  return (
    <div className="w-64 p-4 border rounded-lg shadow-sm hover:shadow-md transition flex flex-col justify-between bg-white">
      <div className="h-40 mb-3 bg-white rounded-md flex items-center justify-center">
        <img
          src={normalizeImageUrl(product?.image) || fallback}
          alt={product?.name || 'product image'}
          loading="lazy"
          className="max-h-full max-w-full object-contain"
          onError={(e) => {
            if (e?.currentTarget?.src !== fallback) e.currentTarget.src = fallback;
          }}
        />
      </div>

      <div className="flex-1">
        <h3 className="font-semibold text-lg mb-1 break-words">{product?.name}</h3>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <p className="font-bold text-lg">{String(primaryPrice).includes('€') ? primaryPrice : `${primaryPrice} €`}</p>
        {shopDisplay && (
          <span className="ml-2 px-0 py-0 rounded text-xs font-semibold text-gray-700 flex items-center">
            {getShopLogoSrc(shopDisplay) ? (
              <img
                src={getShopLogoSrc(shopDisplay)}
                alt={shopDisplay}
                className={getShopLogoClass(shopDisplay)}
                loading="lazy"
                onError={(e) => {
                  // If image fails, show the text label instead
                  const parent = e.currentTarget.parentElement;
                  if (parent) {
                    e.currentTarget.remove();
                    const text = document.createElement('span');
                    text.textContent = shopDisplay;
                    text.className = 'text-xs font-semibold text-gray-700';
                    parent.appendChild(text);
                  }
                }}
              />
            ) : (
              shopDisplay
            )}
          </span>
        )}
      </div>
      {perKgLabel && <p className="text-sm text-gray-500">{perKgLabel}</p>}
    </div>
  );
}
