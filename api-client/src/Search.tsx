import React, { useState } from "react";
import axios from "axios";
import {Paper, Card, CardActionArea, CardMedia, CardContent, Typography, TextField, Button} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";
import Pagination from "@material-ui/lab/Pagination";

const useStyles = makeStyles((theme)=>({
  root: {
    padding: "5%",
    textAlign: "center",
    height: "60%"
  },
  cards: {
    maxWidth: 345,
    margin: "2%"
  },
  grid: {
    width: "100%",
    margin: "auto",
    marginTop: "5%",
    display: "flex",
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-evenly",
    textAlign: "center",
    padding: "auto"
  },
  searchContainer: {
    margin: "auto",
    width: "50%",
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-around"
  },
  paginationContainer: {
    marginTop: "5%",
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-around"

  }
}))

export default function Search(this: any) {

 const classes = useStyles()
  
 const [searchValue, setSearchValue] = useState("")
 const [images, setImages] = useState([])
 const [activeImages, setActive] = useState([])
 const [activePage, setPage] = useState(1)

  const handleOnChange = (event: any) => {
    setSearchValue(event.target.value);
    };

  const handleSearch = () => {
    makeApiCall(searchValue);
    };

  const makeApiCall = (searchInput:any) => {
    var searchUrl = `http://127.0.0.1:8000/images/search/`;
    axios.post(searchUrl,{
      tags: searchInput.split(",")
    })
    .then(response => {
      setImages(response.data)
    })
    .catch(error => console.log(error))
    setActive(images.slice(0,9))
      console.log(images)
      console.log(activeImages)  
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value)
    setActive(images.slice(9*(value-1), 9*value))
  }

  function ImageCard(props:any){
    return(
      <Card className={classes.cards}>
        <CardActionArea>
          <CardMedia
            component="img"
            alt="ipfs image"
            image={props.image["ipfsAddress"]}
            title={props.image["label"]}
            width={1/4}
          />
          <CardContent>
            <Typography gutterBottom variant="h5" component="h2">
              {props.image["label"]}
            </Typography>
            <Typography variant="body2" color="textSecondary" component="p">
              Tags: {props.image["tags"]?props.image["tags"].substring(1, props.image["tags"].length-1):"no tags found"}
            </Typography>
          </CardContent>
        </CardActionArea>
      </Card>
    )
  }

    return (
      <Paper className={classes.root} elevation={10}>
      <Typography variant='h2' component='h2' gutterBottom>Veritas Image Search for Publications</Typography>
      <div className={classes.searchContainer}>
      <TextField
        name="text"
        type="text"
        placeholder="Search"
        onChange={event => handleOnChange(event)}
        value={searchValue}
        fullWidth={true}
      />
        <Button variant="contained" color="primary" onClick={handleSearch}>Search</Button>
      </div>
      {Math.trunc(images.length/9)!==0 && 
        <div className={classes.paginationContainer}><Pagination count={Math.trunc(images.length/9)} page={activePage} onChange={handlePageChange} /></div>
      }
      {activeImages ? (
        <div className={classes.grid}>
        {activeImages.map((image, index) => (
        <ImageCard
          key={index}
          image={image}
          />
        ))}
        </div>
        ) : (
        <p>Try searching for an image from our server</p>
        )
      }
      </Paper>
      );
}