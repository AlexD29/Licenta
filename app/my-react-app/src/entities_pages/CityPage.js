import React, { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./EntityPage.css";
import Footer from "../Footer";
import ArticlesList from "./ArticlesList";

function formatPopulation(population) {
  return population.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

export {formatPopulation};

const CityPage = ({ userId }) => {
  const { id, page } = useParams();
  const currentPage = parseInt(page, 10) || 1;
  const [city, setCity] = useState(null);

  useEffect(() => {
    const fetchCity = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/city/${id}`,
          {
            params: { user_id: userId || null },
          }
        );
        setCity(response.data);
        console.log(city);
      } catch (error) {
        console.error("Error fetching city:", error);
      }
    };
    fetchCity();
  }, [userId, id]);

  const handleAddFavorite = async (city) => {
    try {
      if (!userId) {
        alert("You need to log in to add favorites.");
        return;
      }

      const action = city.isFavorite ? "remove" : "add";

      await axios.post("http://localhost:8000/api/favorites", {
        user_id: userId,
        entity_id: city.id,
        entity_type: city.entity_type,
        action: action,
      });
      setCity({ ...city, isFavorite: !city.isFavorite });
    } catch (error) {
      console.error("Error updating favorites:", error);
    }
  };

  if (!city) return <div>Loading...</div>;

  return (
    <div className="container">
      <div className="entity-page-first-part">
        <div className="entity-first-part-centered">
          <div className="background-div city"></div>
          <div className="profile-info">
            <div className="info-first-column">
              <img
                src={city.image_url}
                alt={city.name}
                className="entity-profile-picture city-picture"
              />
              <h1 className="profile-name">{city.name}</h1>
              <div className="population-info">
                <h3>Populatie</h3>
                <div className="population-row">
                  <span>
                    <svg
                      className="population-svg"
                      width="48"
                      height="48"
                      viewBox="0 0 48 48"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M43.217 23.783C42.3705 22.9367 41.3716 22.2581 40.273 21.783C41.0126 21.2564 41.6335 20.5805 42.0957 19.799C42.5578 19.0175 42.8509 18.1478 42.956 17.246C43.0611 16.3442 42.9758 15.4303 42.7058 14.5635C42.4357 13.6967 41.9868 12.8961 41.3881 12.2136C40.7894 11.531 40.0542 10.9817 39.23 10.6009C38.4058 10.2202 37.5108 10.0166 36.603 10.0032C35.6952 9.9899 34.7947 10.1671 33.9596 10.5235C33.1245 10.8798 32.3735 11.4073 31.755 12.072C31.3269 10.3387 30.3306 8.79882 28.9249 7.69808C27.5192 6.59734 25.7854 5.99924 24 5.99924C22.2146 5.99924 20.4808 6.59734 19.0751 7.69808C17.6694 8.79882 16.6731 10.3387 16.245 12.072C15.6266 11.4065 14.8755 10.8783 14.0401 10.5213C13.2047 10.1644 12.3038 9.98674 11.3954 9.99987C10.4871 10.013 9.59163 10.2166 8.76694 10.5976C7.94224 10.9785 7.20667 11.5283 6.60779 12.2113C6.00891 12.8944 5.56006 13.6956 5.29024 14.563C5.02043 15.4304 4.93567 16.3448 5.04144 17.2471C5.14721 18.1493 5.44116 19.0193 5.90428 19.8008C6.3674 20.5824 6.98938 21.258 7.73 21.784C6.0298 22.5209 4.58183 23.7383 3.56391 25.2866C2.54598 26.835 2.00243 28.647 2 30.5V35C2.00159 36.3256 2.52888 37.5964 3.46622 38.5338C4.40356 39.4711 5.6744 39.9984 7 40H14.026C14.4879 40.6188 15.0874 41.1216 15.7771 41.4688C16.4668 41.8159 17.2279 41.9978 18 42H30C30.7721 41.9978 31.5332 41.8159 32.2229 41.4688C32.9126 41.1216 33.5121 40.6188 33.974 40H41C42.3256 39.9984 43.5964 39.4711 44.5338 38.5338C45.4711 37.5964 45.9984 36.3256 46 35V30.5C46.0034 29.252 45.7592 28.0157 45.2815 26.8627C44.8038 25.7097 44.1021 24.6629 43.217 23.783V23.783ZM36.5 12C37.39 12 38.26 12.2639 39.0001 12.7584C39.7401 13.2529 40.3169 13.9557 40.6575 14.7779C40.9981 15.6002 41.0872 16.505 40.9135 17.3779C40.7399 18.2508 40.3113 19.0526 39.682 19.682C39.0526 20.3113 38.2508 20.7399 37.3779 20.9135C36.505 21.0872 35.6002 20.9981 34.7779 20.6575C33.9557 20.3169 33.2529 19.7401 32.7584 19.0001C32.2639 18.26 32 17.39 32 16.5C32.0013 15.3069 32.4759 14.1631 33.3195 13.3195C34.1631 12.4759 35.3069 12.0013 36.5 12V12ZM31.146 22.654C30.2542 21.8872 29.245 21.2687 28.157 20.822C29.0339 20.2852 29.8 19.5857 30.414 18.761C30.8682 19.9788 31.6761 21.0329 32.734 21.788C32.1786 22.026 31.6469 22.316 31.146 22.654V22.654ZM24 8C25.1867 8 26.3467 8.3519 27.3334 9.01119C28.3201 9.67048 29.0892 10.6075 29.5433 11.7039C29.9974 12.8003 30.1162 14.0067 29.8847 15.1705C29.6532 16.3344 29.0818 17.4035 28.2426 18.2426C27.4035 19.0818 26.3344 19.6532 25.1705 19.8847C24.0067 20.1162 22.8003 19.9974 21.7039 19.5433C20.6075 19.0892 19.6705 18.3201 19.0112 17.3334C18.3519 16.3467 18 15.1867 18 14C18.0016 12.4092 18.6342 10.884 19.7591 9.75912C20.884 8.63424 22.4092 8.00159 24 8V8ZM16.854 22.654C16.3531 22.316 15.8214 22.026 15.266 21.788C16.3239 21.0329 17.1318 19.9788 17.586 18.761C18.2 19.5857 18.9661 20.2852 19.843 20.822C18.755 21.2687 17.7458 21.8872 16.854 22.654V22.654ZM7 16.5C7 15.61 7.26392 14.74 7.75839 13.9999C8.25285 13.2599 8.95566 12.6831 9.77792 12.3425C10.6002 12.002 11.505 11.9128 12.3779 12.0865C13.2508 12.2601 14.0526 12.6887 14.682 13.318C15.3113 13.9474 15.7399 14.7492 15.9135 15.6221C16.0872 16.495 15.9981 17.3998 15.6575 18.2221C15.3169 19.0443 14.7401 19.7472 14.0001 20.2416C13.26 20.7361 12.39 21 11.5 21C10.3069 20.9987 9.16311 20.5241 8.31948 19.6805C7.47585 18.8369 7.00132 17.6931 7 16.5ZM7 38C6.20435 38 5.44129 37.6839 4.87868 37.1213C4.31607 36.5587 4 35.7957 4 35V30.5C3.99807 29.1651 4.35299 27.8539 5.02803 26.7022C5.70306 25.5505 6.67366 24.6002 7.83934 23.9497C9.00502 23.2991 10.3234 22.972 11.658 23.0021C12.9926 23.0322 14.2949 23.4185 15.43 24.121C13.8566 26.0683 12.9988 28.4965 13 31V37C12.9997 37.3358 13.0332 37.6709 13.1 38H7ZM33 37C33 37.7957 32.6839 38.5587 32.1213 39.1213C31.5587 39.6839 30.7956 40 30 40H18C17.2044 40 16.4413 39.6839 15.8787 39.1213C15.3161 38.5587 15 37.7957 15 37V31C15 28.6131 15.9482 26.3239 17.636 24.636C19.3239 22.9482 21.6131 22 24 22C26.3869 22 28.6761 22.9482 30.364 24.636C32.0518 26.3239 33 28.6131 33 31V37ZM44 35C44 35.7957 43.6839 36.5587 43.1213 37.1213C42.5587 37.6839 41.7956 38 41 38H34.9C34.9668 37.6709 35.0003 37.3358 35 37V31C35.0012 28.4965 34.1434 26.0683 32.57 24.121C33.7054 23.4202 35.0074 23.0353 36.3414 23.006C37.6753 22.9766 38.993 23.304 40.1581 23.9543C41.3232 24.6045 42.2936 25.5541 42.969 26.7048C43.6444 27.8555 44.0003 29.1657 44 30.5V35Z"
                        fill="black"
                      ></path>
                    </svg>
                  </span>
                  <p className="profile-birth">
                    {formatPopulation(city.population)} locuitori
                  </p>
                </div>
              </div>
              {city.mayor && (
                <div>
                  <h3>Primar</h3>
                  <Link
                    className="entity-profile-link"
                    to={`/politician/${city.mayor.id}`}
                  >
                    <div className="entity-profile">
                      <img
                        src={city.mayor.image_url}
                        alt={`${city.mayor.name}`}
                        className="entity-profile-picture-mini"
                      />
                      <p>{city.mayor.name}</p>
                    </div>
                  </Link>
                </div>
              )}
            </div>
            <div className="info-second-column">
              <div className="second-column-first-row">
                <div className="entity-big-text">{city.description}</div>
                <div className="profile-button-div-political-party">
                  <button
                    className={`follow-button-profile ${
                      !userId ? "inactive" : city.isFavorite ? "remove" : "add"
                    }`}
                    onClick={() => handleAddFavorite(city)}
                    disabled={!userId}
                  >
                    {city.isFavorite ? "Nu mai urmări" : "Urmarește"}
                  </button>
                </div>
              </div>
              <div className="city-description">
                <h3>Despre</h3>
                <p>{city.description}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="entity-second-part">
        <div className="first-part"></div>
        <ArticlesList entity_id={id} entity_type="city" currentPage={currentPage} />
      </div>
      <Footer />
    </div>
  );
};

export default CityPage;
