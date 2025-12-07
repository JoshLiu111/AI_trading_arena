import { Link } from "react-router-dom";

const Nav = () => {
  return (
    <div className="top-nav">
      <Link to="/">Home</Link>
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/learn-more">Learn More</Link>
    </div>
  );
};

export default Nav;
