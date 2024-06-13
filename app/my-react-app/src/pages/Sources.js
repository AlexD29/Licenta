import React from "react";
import Entities from "./Entities";

const Sources = () => {
  return <Entities userId={2} entityType="source" apiUrl="http://localhost:8000/api/sources_articles" isSource={true} />;
};

export default Sources;
