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
                    boxShadow: '0 2px 16px rgba(0,0,0,0.2)',
                    textAlign: 'center'
                }}
            >
                <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Pirkinių krepšelis</h2>
                {cart.length === 0 ? (
                    <p>Krepšelis tuščias!</p>
                ) : (
                    <ul style={{ maxHeight: '260px', overflowY: 'auto', marginBottom: '1rem' }}>
                        {cart.map((item, idx) => (
                            <li key={idx}>
                                {item.name} 
                                <span style={{ color: '#888', fontSize: '0.95em', marginLeft: 8 }}>
                                    ({item.shop || item.shop_name})
                                </span>
                                - {item.shelf_price}€
                                <button onClick={() => onRemove(idx)} style={{ marginLeft: '10px' }}>Pašalinti</button>
                            </li>
                        ))}
                    </ul>
                )}
                <button
                    onClick={onClose}
                    className="mt-6 px-4 py-2 rounded bg-red-600 text-white font-semibold hover:bg-red-700 transition"
                >
                    Uždaryti
                </button>
            </div>
        </div>
    );
}