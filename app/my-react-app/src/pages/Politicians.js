import React from "react";
import Entities from "./Entities";

const Politicians = () => {
  return <Entities userId={2} entityType="politician" apiUrl="http://localhost:8000/api/politician_articles" />;
};

export default Politicians;
