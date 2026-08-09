function App() {
  return (
    <main className="min-h-screen bg-orange-50 text-slate-900">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 py-16 text-center">
        <span className="mb-4 rounded-full bg-orange-100 px-4 py-2 text-sm font-medium text-orange-700">
          ESTELART Platform
        </span>

        <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-950 md:text-6xl">
          Plataforma comercial para cotillón, insumos creativos y clientes
          mayoristas.
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
          Catálogo personalizado, pedidos, combos, promociones, métricas,
          reportes y futura integración con asistente IA.
        </p>

        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          <a
            href="#catalogo"
            className="rounded-xl bg-orange-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-orange-700"
          >
            Ver catálogo
          </a>

          <a
            href="#mayoristas"
            className="rounded-xl border border-orange-300 bg-white px-6 py-3 text-sm font-semibold text-orange-700 shadow-sm transition hover:bg-orange-100"
          >
            Acceso mayoristas
          </a>
        </div>
      </section>
    </main>
  );
}

export default App;
