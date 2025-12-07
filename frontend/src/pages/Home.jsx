import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  const handleStartCompetition = () => {
    navigate("/dashboard");
  };

  const handleLearnMore = () => {
    navigate("/learn-more");
  };

  return (
    <div className="hero-container">
      <div className="hero-content">
        <h1 className="hero-title">Stock Trading Arena</h1>
        <p className="hero-subtitle">
          AI vs Human Stock Trading Competition
        </p>
        <p className="hero-description">
          Compete against AI traders in real-time stock trading. Test your skills, make strategic decisions, and see who comes out on top in this exciting trading competition.
        </p>
        
        <div className="hero-buttons">
          <button
            onClick={handleStartCompetition}
            className="btn-primary"
          >
            🚀 Start Competition
          </button>
          
          <button
            onClick={handleLearnMore}
            className="btn-secondary"
          >
            📚 Learn More
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
