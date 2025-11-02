import Image from "next/image";

export default function ProductCard({ product }) {
  return (
    <div className="p-4 border rounded-lg shadow-sm hover:shadow-md transition">
      <Image
        src={product.image}
        alt={product.name}
        width={300}
        height={200}
        className="h-40 object-contain rounded-md mb-3"
      />
      <h3 className="font-semibold text-lg">{product.name}</h3>
      <p className="text-sm text-gray-500">{product.store}</p>
      <p className="font-bold">{product.price} €</p>
    </div>
  );
}
