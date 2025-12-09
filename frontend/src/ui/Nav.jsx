import { Link } from "react-router-dom";

const Nav = () => {
  return (
    <div className="top-nav">
      <Link to="/" className="nav-brand">Stock Trading Arena</Link>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/learn-more">Learn More</Link>
      </div>
    </div>
  );
};

export default Nav;
