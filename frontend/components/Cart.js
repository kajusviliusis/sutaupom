export default function Cart({ cart, onClose, onRemove }) {
    return (
        <div
            className="modal-overlay"
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                background: 'rgba(0,0,0,0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}
        >
            <div
                className="modal"
                style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '32px',
                    minWidth: '320px',
                    boxShadow: '0 8px 30px rgba(0,0,0,0.25)',
                    textAlign: 'center'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'center', marginBottom: '1rem' }}>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        width="28"
                        height="28"
                        aria-hidden="true"
                        style={{ display: 'block' }}
                    >
                        <path fill="#000" d="M7 4H3v2h2l3.6 7.59-1.35 2.45A1 1 0 0 0 8.9 17h8.45v-2H9.7l.93-1.68L18.1 6H7V4z" />
                        <circle fill="#000" cx="10" cy="20" r="1" />
                        <circle fill="#000" cx="18" cy="20" r="1" />
                    </svg>
                    <h2 style={{ fontSize: '1.5rem', margin: 0, fontWeight: 700 }}>Pirkinių krepšelis</h2>
                </div>
                {cart.length === 0 ? (
                    <p>Krepšelis tuščias!</p>
                ) : (
                    <ul style={{ maxHeight: '260px', overflowY: 'auto', marginBottom: '1rem', padding: 0, listStyle: 'none' }}>
                        {cart.map((item, idx) => (
                            <li
                                key={idx}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    padding: '10px 0',
                                    borderBottom: '1px solid #f2f2f2'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12, textAlign: 'left', flex: 1, minWidth: 0 }}>
                                    <img
                                        src={item.image || item.image_url || item.img || item.picture || '/images/placeholder-product.png'}
                                        alt={item.name || 'product'}
                                        style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 8 }}
                                    />
                                    <div style={{ overflow: 'hidden' }}>
                                        <div style={{ fontWeight: 600, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{item.name}</div>
                                        <div style={{ color: '#888', fontSize: '0.9em', marginTop: 4 }}>
                                            {item.shop || item.shop_name}
                                        </div>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginLeft: 16 }}>
                                    <div style={{ fontWeight: 600 }}>{item.shelf_price}€</div>
                                    <button
                                        onClick={() => onRemove(idx)}
                                        className="px-3 py-1 rounded bg-black text-white text-sm hover:bg-gray-800 transition"
                                        style={{ border: 'none', cursor: 'pointer' }}
                                    >
                                        Pašalinti
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
                <button
                    onClick={onClose}
                    className="mt-6 px-4 py-2 rounded bg-black text-white font-semibold hover:bg-gray-800 transition"
                    style={{ border: 'none', cursor: 'pointer' }}
                >
                    Uždaryti
                </button>
            </div>
        </div>
    );
}