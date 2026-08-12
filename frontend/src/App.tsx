import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Landing from "./pages/Home";
import NewInvestigation from "./pages/NewInvestigation";
import History from "./pages/History";
import Results from "./pages/Results";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Landing />}
        />

        <Route
          path="/investigate"
          element={<NewInvestigation />}
        />

        <Route
          path="/history"
          element={<History />}
        />

        <Route
          path="/investigate/:investigationId"
          element={<Results />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;