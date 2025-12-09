import { Link } from "react-router-dom";

const LearnMore = () => {
  return (
    <div className="learn-more-container">
      <div className="learn-more-content">
        <div className="learn-more-header">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
          <h1>Trading Strategies Guide</h1>
          <p className="subtitle">
            Understanding different trading timeframes and key indicators
          </p>
        </div>

        <div className="strategy-sections">
          {/* Scalping (Ultra Short-term) */}
          <section className="strategy-section">
            <h2>Scalping (Ultra Short-term Trading)</h2>
            <div className="strategy-info">
              <p className="timeframe">Timeframe: Seconds to minutes</p>
              <p className="description">
                Scalping is the shortest-term trading strategy, where traders aim to profit from 
                small price movements. Positions are typically held for seconds to a few minutes, 
                with traders making dozens or hundreds of trades per day.
              </p>
              
              <div className="key-indicators">
                <h3>Key Indicators:</h3>
                <ul>
                  <li><strong>Bid-Ask Spread:</strong> The difference between buy and sell prices. 
                  Scalpers need tight spreads to be profitable.</li>
                  <li><strong>Volume:</strong> High trading volume ensures liquidity and allows 
                  quick entry and exit.</li>
                  <li><strong>Level II Quotes:</strong> Real-time order book data showing buy and 
                  sell orders at different price levels.</li>
                  <li><strong>Tick Volume:</strong> Number of price changes per unit of time, 
                  indicating market activity.</li>
                  <li><strong>Time & Sales:</strong> Real-time transaction data showing actual 
                  trades executed.</li>
                  <li><strong>VWAP (Volume Weighted Average Price):</strong> Average price 
                  weighted by volume, used as a reference point for entry/exit.</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Day Trading (Short-term) */}
          <section className="strategy-section">
            <h2>Day Trading (Short-term Trading)</h2>
            <div className="strategy-info">
              <p className="timeframe">Timeframe: Minutes to hours (same day)</p>
              <p className="description">
                Day trading involves opening and closing positions within the same trading day. 
                Day traders capitalize on intraday price movements and avoid holding positions 
                overnight to minimize risk from gap events.
              </p>
              
              <div className="key-indicators">
                <h3>Key Indicators:</h3>
                <ul>
                  <li><strong>Moving Averages (MA):</strong> 9, 20, 50, and 200-period moving 
                  averages help identify trends and support/resistance levels.</li>
                  <li><strong>RSI (Relative Strength Index):</strong> Momentum oscillator (0-100) 
                  indicating overbought (above 70) or oversold (below 30) conditions.</li>
                  <li><strong>MACD (Moving Average Convergence Divergence):</strong> Trend-following 
                  momentum indicator showing relationship between two moving averages.</li>
                  <li><strong>Bollinger Bands:</strong> Volatility bands around a moving average, 
                  indicating potential price breakouts or reversals.</li>
                  <li><strong>Volume Profile:</strong> Distribution of trading volume at different 
                  price levels, identifying support and resistance zones.</li>
                  <li><strong>Intraday Support/Resistance:</strong> Key price levels where the 
                  stock has previously reversed direction.</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Swing Trading (Medium-term) */}
          <section className="strategy-section">
            <h2>Swing Trading (Medium-term Trading)</h2>
            <div className="strategy-info">
              <p className="timeframe">Timeframe: Days to weeks</p>
              <p className="description">
                Swing trading captures price swings or "waves" in the market. Traders hold 
                positions for several days to weeks, aiming to profit from short-to-medium-term 
                price movements. This strategy balances the frequency of day trading with the 
                patience of position trading.
              </p>
              
              <div className="key-indicators">
                <h3>Key Indicators:</h3>
                <ul>
                  <li><strong>Trend Lines:</strong> Lines connecting price highs or lows to 
                  identify trend direction and potential reversal points.</li>
                  <li><strong>Fibonacci Retracements:</strong> Horizontal lines indicating 
                  potential support/resistance levels based on Fibonacci ratios (23.6%, 38.2%, 
                  50%, 61.8%).</li>
                  <li><strong>Stochastic Oscillator:</strong> Momentum indicator comparing closing 
                  price to price range over a period, identifying overbought/oversold conditions.</li>
                  <li><strong>ADX (Average Directional Index):</strong> Measures trend strength 
                  (not direction), with values above 25 indicating strong trends.</li>
                  <li><strong>Chart Patterns:</strong> Head and shoulders, triangles, flags, and 
                  pennants that suggest future price movements.</li>
                  <li><strong>Volume Analysis:</strong> Confirming price movements with volume 
                  trends - increasing volume on breakouts validates the move.</li>
                  <li><strong>Support and Resistance Levels:</strong> Historical price levels 
                  where the stock has reversed or consolidated.</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Position Trading (Long-term) */}
          <section className="strategy-section">
            <h2>Position Trading (Long-term Trading)</h2>
            <div className="strategy-info">
              <p className="timeframe">Timeframe: Weeks to months or years</p>
              <p className="description">
                Position trading is a long-term strategy where traders hold positions for weeks, 
                months, or even years. This approach focuses on fundamental analysis and major 
                market trends, requiring patience and a strong understanding of market cycles 
                and economic factors.
              </p>
              
              <div className="key-indicators">
                <h3>Key Indicators:</h3>
                <ul>
                  <li><strong>Fundamental Analysis:</strong> Company financials, earnings, revenue 
                  growth, debt levels, and management quality.</li>
                  <li><strong>P/E Ratio (Price-to-Earnings):</strong> Stock price divided by 
                  earnings per share, indicating valuation relative to earnings.</li>
                  <li><strong>PEG Ratio (Price/Earnings to Growth):</strong> P/E ratio divided by 
                  earnings growth rate, providing growth-adjusted valuation.</li>
                  <li><strong>Moving Averages:</strong> Long-term moving averages (50, 100, 200-day) 
                  to identify major trends and trend reversals.</li>
                  <li><strong>MACD (Long-term):</strong> Weekly or monthly MACD for identifying 
                  major trend changes.</li>
                  <li><strong>Economic Indicators:</strong> GDP growth, inflation rates, interest 
                  rates, and employment data affecting market direction.</li>
                  <li><strong>Sector Analysis:</strong> Industry trends, competitive positioning, 
                  and sector rotation patterns.</li>
                  <li><strong>Market Cycles:</strong> Understanding bull and bear market phases, 
                  and economic cycles (expansion, peak, contraction, trough).</li>
                  <li><strong>Dividend Yield:</strong> Annual dividend payment divided by stock 
                  price, important for income-focused investors.</li>
                </ul>
              </div>
            </div>
          </section>
        </div>

        <div className="strategy-comparison">
          <h2>Strategy Comparison</h2>
          <div className="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>Strategy</th>
                  <th>Holding Period</th>
                  <th>Time Commitment</th>
                  <th>Risk Level</th>
                  <th>Capital Required</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Scalping</td>
                  <td>Seconds to minutes</td>
                  <td>Full-time, constant monitoring</td>
                  <td>Very High</td>
                  <td>High (due to frequent trading costs)</td>
                </tr>
                <tr>
                  <td>Day Trading</td>
                  <td>Same day</td>
                  <td>Full-time during market hours</td>
                  <td>High</td>
                  <td>Moderate to High</td>
                </tr>
                <tr>
                  <td>Swing Trading</td>
                  <td>Days to weeks</td>
                  <td>Part-time, daily monitoring</td>
                  <td>Moderate</td>
                  <td>Moderate</td>
                </tr>
                <tr>
                  <td>Position Trading</td>
                  <td>Weeks to years</td>
                  <td>Part-time, periodic review</td>
                  <td>Moderate to Low</td>
                  <td>Low to Moderate</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="general-tips">
          <h2>General Trading Principles</h2>
          <ul>
            <li><strong>Risk Management:</strong> Never risk more than 1-2% of your capital on a 
            single trade. Use stop-loss orders to limit potential losses.</li>
            <li><strong>Position Sizing:</strong> Adjust position size based on volatility and 
            your confidence level in the trade.</li>
            <li><strong>Diversification:</strong> Don't put all your capital in one stock or sector. 
            Spread risk across different positions.</li>
            <li><strong>Emotional Control:</strong> Stick to your trading plan. Avoid making 
            decisions based on fear or greed.</li>
            <li><strong>Continuous Learning:</strong> Markets evolve constantly. Stay updated with 
            market news, economic events, and new trading techniques.</li>
            <li><strong>Record Keeping:</strong> Maintain a trading journal to track your trades, 
            analyze what works, and learn from mistakes.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LearnMore;
