import { readFile } from "fs/promises";
import { join } from "path";

export async function GET(request) {
  try {
    const filePath = join(process.cwd(), "data/products.json"); // kelias i json faila
    const fileContents = await readFile(filePath, "utf-8");
    const products = JSON.parse(fileContents);

    const url = new URL(request.url);
    const search = url.searchParams.get("query")

    let filteredProducts = products;
    if (search) {
      const query = search.trim().toLowerCase();
      filteredProducts = products.filter((p) =>
        p.name.toLowerCase().includes(query)
      );
    }

    // 6. Grąžiname rastus produktus kaip JSON atsakymą
    return new Response(JSON.stringify(filteredProducts), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("Klaida skaitant failą:", err);

    // Jei kažkas nepavyko – grąžiname klaidos pranešimą
    return new Response(
      JSON.stringify({ error: "Nepavyko perskaityti produktų failo." }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
