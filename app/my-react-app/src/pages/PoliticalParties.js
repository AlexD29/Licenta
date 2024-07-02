import React from "react";
import Entities from "./Entities";

const PoliticalParties = ({userId}) => {
  return <Entities userId={userId} entityType="political-party" apiUrl="http://localhost:8000/api/political_parties_articles" />;
};

export default PoliticalParties;
