import React from "react";
import Entities from "./Entities";

const PoliticalParties = () => {
  return <Entities userId={2} entityType="political-party" apiUrl="http://localhost:8000/api/political_parties_articles" />;
};

export default PoliticalParties;
