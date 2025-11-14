import React, { useState } from "react";
import { Card, CardHeader, CardContent } from "./ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Label } from "./ui/Label";
import { api } from "../lib/api";
import { setAuthToken, setUser, type User } from "../lib/auth";

interface LoginProps {
  onLoginSuccess: (user: User) => void;
}

export default function Login({ onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.login(email, password);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Login failed");
      }

      const data = await res.json();
      setAuthToken(data.access_token);
      setUser(data.user);
      onLoginSuccess(data.user);
    } catch (err: any) {
      setError(err?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.register({
        email,
        password,
        full_name: fullName || undefined,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Registration failed");
      }

      // After registration, automatically log in
      const loginRes = await api.login(email, password);
      if (!loginRes.ok) {
        throw new Error("Registration successful but login failed");
      }

      const data = await loginRes.json();
      setAuthToken(data.access_token);
      setUser(data.user);
      onLoginSuccess(data.user);
    } catch (err: any) {
      setError(err?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-2xl font-bold text-center">
            {isRegistering ? "Create Account" : "Login"}
          </h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={isRegistering ? handleRegister : handleLogin}>
            {isRegistering && (
              <div className="mb-4">
                <Label htmlFor="fullName">Full Name (optional)</Label>
                <Input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Doe"
                />
              </div>
            )}
            <div className="mb-4">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="mb-4">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            {error && (
              <div className="mb-4 text-sm text-red-500">{error}</div>
            )}
            <Button
              type="submit"
              className="w-full mb-2"
              disabled={loading}
            >
              {loading
                ? isRegistering
                  ? "Creating Account..."
                  : "Logging in..."
                : isRegistering
                ? "Create Account"
                : "Login"}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={() => {
                setIsRegistering(!isRegistering);
                setError(null);
              }}
            >
              {isRegistering
                ? "Already have an account? Login"
                : "Don't have an account? Register"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

