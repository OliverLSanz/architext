"use client"

import { useState } from "react";
import { signup } from "@/architextSDK";
import { useStore } from "@/state";
import Link from "next/link";
import { useRouter } from 'next/navigation'

export default function Home() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const socket = useStore((state) => state.socket)
  const router = useRouter()

  // Maneja el evento submit del formulario.
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Aquí podrías llamar a tu API o servicio de autenticación.
    console.log("Name:", name);
    console.log("Email:", email);
    console.log("Password:", password);
    const response = await signup(socket, { name: name, email, password: password })
    console.log(response)
    if(response.success) {
      router.push('login')
    } else {
      setError("Error: " + response.error)
    }
  };

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <div>Crea una cuenta en Architext</div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-sm">
          {
            error &&
            <div>{error}</div>
          }
          <label htmlFor="name">
            Username
          </label>
          <input
            id="name"
            // type=""
            className="border border-gray-300 px-3 py-2 rounded"
            placeholder=""
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <label htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            className="border border-gray-300 px-3 py-2 rounded"
            placeholder="tucorreo@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            className="border border-gray-300 px-3 py-2 rounded"
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            type="submit"
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            Login
          </button>
        </form>
        <Link href='/login' className='text-blue-500 hover:underline'>Inicia sesión</Link>
      </main>

      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        Welcome to Architext
      </footer>
    </div>
  );
}