import React from "react";
import Entities from "./Entities";

const City = () => {
  return <Entities userId={2} entityType="city" apiUrl="http://localhost:8000/api/cities_articles" />;
};

export default City;
