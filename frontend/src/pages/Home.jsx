import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  /**
   * Handle Start Competition button click
   * Only navigates to dashboard - does not start competition or perform any other operations
   */
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
            Try it now
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
