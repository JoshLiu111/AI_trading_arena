import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import StockDetail from "./pages/StockDetail";
import AccountDetail from "./pages/AccountDetail";
import LearnMore from "./pages/LearnMore";
import { Nav } from "./components";

function App() {
  return (
    <Router>
      <Nav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/stock/:ticker" element={<StockDetail />} />
        <Route path="/account/:accountId" element={<AccountDetail />} />
        <Route path="/learn-more" element={<LearnMore />} />
      </Routes>
    </Router>
  );
}

export default App;
