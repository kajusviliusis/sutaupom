import { readFile } from "fs/promises";
import { join } from "path";

export async function GET() {
  try {
    const filePath = join(process.cwd(), "data/products.json"); // kelias i json faila
    const fileContents = await readFile(filePath, "utf-8");
    const products = JSON.parse(fileContents);

    return new Response(JSON.stringify(products), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Klaida skaitant products.json:", error);
    return new Response(JSON.stringify({ error: "Failo nepavyko nuskaityti" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
