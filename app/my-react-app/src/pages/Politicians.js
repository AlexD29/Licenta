import React from "react";
import Entities from "./Entities";

const Politicians = ({userId}) => {
  return <Entities userId={userId} entityType="politician" apiUrl="http://localhost:8000/api/politician_articles" />;
};

export default Politicians;
