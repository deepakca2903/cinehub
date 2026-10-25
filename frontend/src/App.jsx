import React from 'react';
import { useEffect, useMemo, useState } from "react";
import { Link, Route, Routes, useNavigate, useParams, useSearchParams } from "react-router-dom";
import api from "./api";

function Header({ user, onLogout }) {
  return <header className="topbar">
    <Link className="brand" to="/"><span className="brand-icon">C</span> Cine<span>Hub</span></Link>
    <nav><Link to="/">Movies</Link><Link to="/bookings">My bookings</Link>
      {user ? <><span className="welcome">Hi, {user.name}</span><button className="nav-button" onClick={onLogout}>Logout</button></> : <Link className="nav-cta" to="/login">Login</Link>}
    </nav>
  </header>;
}

function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("cinehub_user")); } catch { return null; }
  });
  const [notice, setNotice] = useState("");
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem("cinehub_token");
    localStorage.removeItem("cinehub_user");
    setUser(null); setNotice("You have logged out."); navigate("/");
  };
  const loginDone = (token, userData) => {
    localStorage.setItem("cinehub_token", token);
    localStorage.setItem("cinehub_user", JSON.stringify(userData));
    setUser(userData); setNotice("Welcome to CineHub!"); navigate("/");
  };
  return <div className="app-shell">
    <Header user={user} onLogout={logout} />
    {notice && <div className="notice"><span>{notice}</span><button onClick={() => setNotice("")}>×</button></div>}
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/movies/:id" element={<MovieDetails user={user} />} />
      <Route path="/shows/:id/seats" element={<SeatBooking user={user} />} />
      <Route path="/login" element={<AuthPage mode="login" onDone={loginDone} />} />
      <Route path="/register" element={<AuthPage mode="register" onDone={loginDone} />} />
      <Route path="/bookings" element={<Bookings user={user} />} />
      <Route path="*" element={<main className="container"><h2>Page not found</h2><Link to="/">Back to movies</Link></main>} />
    </Routes>
    <footer>© {new Date().getFullYear()} CineHub · Find your next favourite movie.</footer>
  </div>;
}

function Home() {
  const [movies, setMovies] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    api.get("/api/movies").then(r => setMovies(r.data)).catch(() => setError("Could not load movies. Check that the FastAPI backend and MySQL are running.")).finally(() => setLoading(false));
  }, []);
  const filtered = useMemo(() => movies.filter(m => `${m.title} ${m.genre} ${m.language}`.toLowerCase().includes(search.toLowerCase())), [movies, search]);
  return <main>
    <section className="hero">
      <div className="hero-content">
        <div className="eyebrow">YOUR MOVIE NIGHT STARTS HERE</div>
        <h1>Big stories.<br/><span>Big screen.</span></h1>
        <p>Discover movies, choose your seats, and make it a night to remember.</p>
        <a className="primary-button" href="#movies">Explore movies <span>↘</span></a>
      </div>
      <div className="hero-art"><div className="ticket ticket-back">CINEHUB <b>✦</b></div><div className="ticket ticket-front"><span>ADMIT ONE</span><strong>YOUR<br/>NEXT<br/>FAVOURITE</strong><small>GOOD STORIES LIVE HERE</small></div><div className="orb"></div></div>
    </section>
    <section id="movies" className="container movies-section">
      <div className="section-heading"><div><div className="eyebrow">NOW SHOWING</div><h2>Find your movie</h2></div>
        <label className="search-box"><span>⌕</span><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search title, genre, language..." /></label>
      </div>
      {loading && <p className="muted">Loading movies…</p>}
      {error && <div className="error-box">{error}</div>}
      {!loading && !error && filtered.length === 0 && <p className="muted">No movies found. Try another search.</p>}
      <div className="movie-grid">{filtered.map(movie => <MovieCard key={movie.id} movie={movie} />)}</div>
    </section>
  </main>;
}

function MovieCard({ movie }) {
  return <article className="movie-card">
    <Link to={`/movies/${movie.id}`} className="poster-wrap">
      {movie.poster_url ? <img src={movie.poster_url} alt={`${movie.title} poster`} onError={e => { e.currentTarget.style.display = "none"; }} /> : null}
      <div className="poster-fallback"><span>✦</span><strong>{movie.title}</strong></div>
      <span className="rating">★ {Number(movie.rating).toFixed(1)}</span>
      <span className="poster-overlay">View details ↗</span>
    </Link>
    <div className="movie-card-info"><div className="movie-meta">{movie.genre} <span>·</span> {movie.duration_minutes} min</div><h3><Link to={`/movies/${movie.id}`}>{movie.title}</Link></h3><p>{movie.language}{movie.release_date ? ` · ${movie.release_date}` : ""}</p></div>
  </article>;
}

function MovieDetails({ user }) {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [shows, setShows] = useState([]);
  const [city, setCity] = useState("Bengaluru");
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([api.get(`/api/movies/${id}`), api.get(`/api/shows?movie_id=${id}`)])
      .then(([m, s]) => { setMovie(m.data); setShows(s.data); })
      .catch(() => setError("Could not load movie details."));
  }, [id]);
  const cities = [...new Set(shows.map(s => s.city))];
  const filteredShows = shows.filter(s => !city || s.city.toLowerCase().includes(city.toLowerCase()));
  if (error) return <main className="container"><div className="error-box">{error}</div></main>;
  if (!movie) return <main className="container"><p className="muted">Loading movie…</p></main>;
  return <main className="container details-page">
    <Link className="back-link" to="/">← All movies</Link>
    <section className="detail-hero">
      <div className="detail-poster">{movie.poster_url && <img src={movie.poster_url} alt={movie.title} />}</div>
      <div className="detail-copy"><div className="eyebrow">MOVIE DETAILS</div><h1>{movie.title}</h1>
        <div className="detail-tags"><span>{movie.genre}</span><span>{movie.language}</span><span>{movie.duration_minutes} minutes</span></div>
        <div className="detail-rating">★ {Number(movie.rating).toFixed(1)} <small>/ 10</small></div>
        <p className="description">{movie.description || "No description available yet."}</p>
        <p className="muted">Release date: {movie.release_date || "Not listed"}</p>
      </div>
    </section>
    <section className="show-section"><div className="section-heading"><div><div className="eyebrow">PICK YOUR SHOW</div><h2>Showtimes & theatres</h2></div>
      <select value={city} onChange={e => setCity(e.target.value)}><option value="">All cities</option>{cities.map(c => <option key={c}>{c}</option>)}</select>
    </div>
    {filteredShows.length === 0 ? <p className="muted">No shows available for this city. Choose another city or add shows as an admin.</p> :
      <div className="show-list">{filteredShows.map(show => <div className="show-row" key={show.id}>
        <div><strong>{show.theatre_name}</strong><p>{show.city} · {show.show_date}</p></div>
        <div className="show-time">{show.show_time.slice(0,5)}</div><div className="show-price">₹{Number(show.price).toFixed(0)}</div>
        <Link className="small-button" to={user ? `/shows/${show.id}/seats` : "/login"}>Select seats →</Link>
      </div>)}</div>}
    </section>
  </main>;
}

function SeatBooking({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => { api.get(`/api/shows/${id}/seats`).then(r => setData(r.data)).catch(e => setMessage(e.response?.data?.detail || "Could not load seats.")); }, [id]);
  const toggle = seat => setSelected(old => old.includes(seat) ? old.filter(s => s !== seat) : old.length >= 10 ? old : [...old, seat]);
  const book = async () => {
    if (!user) return navigate("/login");
    if (!selected.length) return setMessage("Choose at least one seat.");
    setBusy(true); setMessage("");
    try {
      const result = await api.post("/api/bookings", { show_id: Number(id), seats: selected });
      setMessage(`Booking confirmed! Booking IDs: ${result.data.map(b => b.id).join(", ")}`);
      setSelected([]);
      const fresh = await api.get(`/api/shows/${id}/seats`); setData(fresh.data);
    } catch (e) { setMessage(e.response?.data?.detail || "Booking failed. Please try again."); }
    finally { setBusy(false); }
  };
  if (!data) return <main className="container"><p className="muted">{message || "Loading seats…"}</p></main>;
  return <main className="container seat-page"><Link className="back-link" to="/">← Back to movies</Link>
    <div className="section-heading"><div><div className="eyebrow">MAKE IT YOURS</div><h1>Select your seats</h1></div><div className="price-chip">₹{Number(data.price).toFixed(0)} <small>/ seat</small></div></div>
    <div className="seat-layout"><div className="screen">SCREEN THIS WAY</div><div className="seat-grid">{data.seats.map(s => <button key={s.seat_number} disabled={s.status === "BOOKED"} onClick={() => toggle(s.seat_number)} className={`seat ${s.status === "BOOKED" ? "booked" : selected.includes(s.seat_number) ? "selected" : ""}`} title={`${s.seat_number}: ${s.status}`}>{s.seat_number}</button>)}</div>
      <div className="seat-legend"><span><i className="legend-available"></i> Available</span><span><i className="legend-selected"></i> Selected</span><span><i className="legend-booked"></i> Booked</span></div>
    </div>
    <div className="booking-summary"><div><span className="muted">Selected seats</span><strong>{selected.length ? selected.join(", ") : "None selected"}</strong></div><div><span className="muted">Total</span><strong>₹{(Number(data.price) * selected.length).toFixed(2)}</strong></div><button className="primary-button" disabled={busy || !selected.length} onClick={book}>{busy ? "Booking…" : "Confirm booking"}</button></div>
    {message && <div className={message.toLowerCase().includes("failed") || message.toLowerCase().includes("already") ? "error-box" : "notice inline-notice"}>{message}</div>}
    <p className="fine-print">Demo mode: no real payment is collected. Confirming a booking reserves the selected seats in the database.</p>
  </main>;
}

function AuthPage({ mode, onDone }) {
  const isRegister = mode === "register";
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async e => {
    e.preventDefault(); setError(""); setBusy(true);
    try {
      if (isRegister) await api.post("/api/auth/register", { name, email, password });
      const form = new URLSearchParams(); form.append("username", email); form.append("password", password);
      const result = await api.post("/api/auth/login", form, { headers: { "Content-Type": "application/x-www-form-urlencoded" } });
      onDone(result.data.access_token, result.data.user);
    } catch (e) { setError(e.response?.data?.detail || "Could not sign in. Check your details and backend."); }
    finally { setBusy(false); }
  };
  return <main className="auth-page"><form className="auth-card" onSubmit={submit}><div className="eyebrow">{isRegister ? "JOIN THE CLUB" : "WELCOME BACK"}</div><h1>{isRegister ? "Create your account" : "Sign in to CineHub"}</h1><p className="muted">{isRegister ? "Your next movie night is a few steps away." : "Your tickets are waiting."}</p>
    {isRegister && <label>Full name<input required minLength="2" value={name} onChange={e => setName(e.target.value)} placeholder="Your name" /></label>}
    <label>Email address<input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" /></label>
    <label>Password<input required minLength="8" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters" /></label>
    {error && <div className="error-box">{error}</div>}<button className="primary-button full-button" disabled={busy}>{busy ? "Please wait…" : isRegister ? "Create account" : "Login"}</button>
    <p className="auth-switch">{isRegister ? "Already have an account?" : "New to CineHub?"} <Link to={isRegister ? "/login" : "/register"}>{isRegister ? "Login" : "Create account"}</Link></p>
  </form></main>;
}

function Bookings({ user }) {
  const [bookings, setBookings] = useState([]);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  useEffect(() => {
    if (!user) return;
    api.get("/api/bookings/me").then(r => setBookings(r.data)).catch(e => setError(e.response?.data?.detail || "Could not load bookings."));
  }, [user, reload]);
  const cancel = async id => {
    if (!confirm("Cancel this seat booking?")) return;
    try { await api.post(`/api/bookings/${id}/cancel`); setReload(x => x + 1); }
    catch (e) { setError(e.response?.data?.detail || "Cancellation failed."); }
  };
  if (!user) return <main className="container empty-state"><h1>Your bookings</h1><p>Login to see your tickets.</p><Link className="primary-button" to="/login">Login</Link></main>;
  return <main className="container bookings-page"><div className="eyebrow">YOUR PLANS</div><h1>My bookings</h1><p className="muted">Your confirmed seats and past reservations.</p>
    {error && <div className="error-box">{error}</div>}
    {!bookings.length && !error ? <div className="empty-state"><span>🎟️</span><h2>No bookings yet</h2><p>Find a movie and book your first seat.</p><Link className="primary-button" to="/">Explore movies</Link></div> :
      <div className="booking-list">{bookings.map(b => <article className="booking-card" key={b.id}><div className="booking-icon">🎬</div><div className="booking-info"><h3>{b.movie_title}</h3><p>{b.theatre_name} · {b.city}</p><p>{b.show_date} at {b.show_time.slice(0,5)} · Seat {b.seat_number}</p><small>Booking #{b.id}</small></div><div className="booking-end"><strong>₹{Number(b.amount).toFixed(0)}</strong><span className={`status ${b.status.toLowerCase()}`}>{b.status}</span>{b.status === "CONFIRMED" && <button className="text-button" onClick={() => cancel(b.id)}>Cancel</button>}</div></article>)}</div>}
  </main>;
}

export default App;
