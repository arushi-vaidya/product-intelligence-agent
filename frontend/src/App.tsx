import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Navbar from "./components/nav/Navbar";
import Landing from "./pages/Home";
import NewInvestigation from "./pages/NewInvestigation";
import BulkUpload from "./pages/BulkUpload";
import History from "./pages/History";
import Results from "./pages/Results";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

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
          path="/bulk-upload"
          element={<BulkUpload />}
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