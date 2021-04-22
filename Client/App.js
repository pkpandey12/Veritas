/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow
 */

import React, { Component, Fragment } from 'react';
import { StyleSheet, Text, TouchableOpacity, View, PixelRatio, Image, Linking, Dimensions, TextInput, ScrollView, FlatList, Modal } from 'react-native';
import ImageLicker from 'react-native-image-picker';
import { Icon, Container, Header, Left, Button, Body, Title, Right, Thumbnail } from 'native-base';

import Spinner from './components/Spinner';
import Card from './components/Card';
import CachedImage from './components/CachedImage';
import TextContainer from './components/TextContainer';

import * as ImagePicker from 'expo-image-picker';
// import Constants from 'expo-constants';
import * as Permissions from 'expo-permissions';
import moment from 'moment';
import { LogBox } from 'react-native';

import Constants from "expo-constants";
const { manifest } = Constants;

import axios from "axios";


//import FastImage from 'react-native-fast-image'



const api = (typeof manifest.packagerOpts === `object`) && manifest.packagerOpts.dev
  ? manifest.debuggerHost.split(`:`).shift().concat(`:8000`)
  : `https://10.66.233.107:8000`;



// CHANGE THIS LINK TO REFLECT LOCAL NGROK LINK 
const ngroklink = "https://1cfbd6475f17.ngrok.io"

const options = {
  title: 'Select Avatar',
  storageOptions: {
    skipBackup: true,
    path: 'images',
  },
};

const B = (props) => <Text style={{fontWeight: 'bold'}}>{props.children}</Text>

const { height, width } = Dimensions.get('window');

export default class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      avatarSource: null,
      loading: null,
      fetchLoading: true,
      clickUpload: false,
      uploadStatus: false,
      label: '',
      images: [],
      article: '',
      tags: '',
      isVisible: false,
      modalData: {},
      address : null,
      similarImages: [],
      loginModalVisible: true
    };
  }

  //Modal for more image details
  displayModal(show, modalData){
  this.setState({isVisible: show, modalData: modalData});
  console.log("ModalData", modalData);
}

  displayLoginModal(show){
    this.setState({loginModalVisible: show});
    console.log("displayLoginModal called");
}

  componentDidMount() {
    LogBox.ignoreLogs(['VirtualizedLists should never be nested']);
    this.getPermissionAsync();
    console.log(api);
    const config = {
      method: 'GET',
      headers: {
        Accept: 'application/json'
      },
    };
    axios.get(`${ngroklink}/images/`) //--- .then((resp) => resp.json())
      .then((res) => {
        //console.log("GET response", res)
        this.setState({
          images: res.data,
          fetchLoading: false
        })
      })
      .catch((err) => {
        console.log('err', err)
        this.setState({
          fetchLoading: false,
          error: err.message
        });
      })

  }

  getPermissionAsync = async () => {
    if (Constants.platform.ios) {
      console.log("In the permissions func");
      const { status } = await Permissions.askAsync(Permissions.CAMERA_ROLL);
      const { s } = await Permissions.askAsync(Permissions.CAMERA);
      if (status !== 'granted' ) {
        alert('Sorry, we need camera roll permissions to make this work!');
      }
      // if (s !== 'granted' ) {
      //   alert('Sorry, we need camera permissions to make this work!');
      // }
    }
  }

  _pickImage = async () => {
    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      aspect: [4, 3],
      quality: 1,
      exif: true
    });

    console.log(result);

    // var id = crypto.randomBytes(20).toString('hex');

    if (!result.cancelled) {
      const source = { uri: result.uri };
      this.setState({
        uploadStatus: true,
        avatarSource: source,
        uri: result.uri,
        type: result.type,
        name: "YOLO1235.png",
        originalName: "YOLO1235.png"
        });
    }

    global.data = new FormData();

    data.append('file', {
      uri: result.uri,
      type: result.type,
      name:  "YOLO1235.png",
      originalname:  "YOLO1235.png",
    });

    data.append('datetime', result.exif.DateTimeOriginal);

    const config = {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'multipart/form-data',
      },
      body: data,
    };
  };

  upload = async () => {
    this.setState({
      loading: true
    });
    if (!this.state.uploadStatus) {
      this.setState({ loading: null })
      return alert('Image yet to be uploaded')
    }
    if (this.state.label === '') {
      this.setState({ loading: null })
      return alert('Enter image label')
    }
    if (this.state.article === '') {
      this.setState({ loading: null })
      return alert('Enter image article')
    }
    else {
      data.append('label', this.state.label);
      data.append('article', this.state.article);
      data.append('tags', this.state.tags);
      console.log("Trying to upload");
      console.log("this", data)
      const config = {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'multipart/form-data',
        },
        body: data,
      };


      fetch(`${ngroklink}/images/`, config) //
        .then((resp) => resp.json())
        .then((res) => {
          console.log("POST response", res)
          this.setState((prevState) => ({
            label: res.label,
            hash: res.ipfsHash,
            address: res.imgipfsAddress,
            transactionHash: res.transactionHash,
            blockHash: res.blockHash,
            loading: false,
            images: prevState.images.concat(res),
          }))
        })
        .catch((err) => {
          this.setState({
            loading: false,
            error: err.message
          });
        })
    }

  }

  similarImages = async () => {
      console.log("fetching similar images");
      const config = {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'multipart/form-data',
        },
        body: this.state.modalData.imgipfsHash,
      };
      //${this.state.modalData.imgipfsHash}
      //QmduFGqosA52hTwXoqY2VVBAAX6PEJKqYhiXjk9ubRhuhw
      axios.get(`${ngroklink}/images/similar/QmduFGqosA52hTwXoqY2VVBAAX6PEJKqYhiXjk9ubRhuhw`) //--- .then((resp) => resp.json())
        .then((res) => {
          console.log("GET response for similar images", res)
          this.setState({
            // images: res.data,
            // fetchLoading: false
            similarImages: res.data
          })
        })
        .catch((err) => {
          console.log('err', err)
          this.setState({
            error: err.message
          });
        })

  }

  newUploadScreen() {
    return (
      <View style={{ flex: 1, marginTop: 10 }}>
        <View style={{ alignItems: 'center', flex: 1 }}>
          <View style={{ marginTop: '10%', flex: 1 }}>
            <TouchableOpacity onPress={() => this._pickImage()}>
              <View style={[styles.avatar, styles.avatarContainer, { marginBottom: 20 }]}>
                {this.state.avatarSource === null ? <Text>Select a Photo</Text> :
                  <Image style={styles.avatar} source={this.state.avatarSource} />
                }
              </View>
            </TouchableOpacity>

            <View style={{ alignItems: 'center' }}>
              <TextInput
                placeholder="Label"
                onChangeText={(label) => this.setState({ label })}
                style={styles.label}
                underlineColorAndroid="transparent"
              />
            </View>

            <View style={{ alignItems: 'center' }}>
              <TextInput
                placeholder="article"
                onChangeText={(article) => this.setState({ article })}
                style={styles.label}
                underlineColorAndroid="transparent"
              />
            </View>

            <View style={{ alignItems: 'center' }}>
              <TextInput
                placeholder="Tags (separate with commas)"
                onChangeText={(tags) => this.setState({ tags })}
                style={styles.label}
                underlineColorAndroid="transparent"
              />
            </View>

            <View style={{ alignItems: 'center' }}>
              <TouchableOpacity onPress={() => this.upload()} style={[styles.uploadbutton, { justifyContent: 'center', backgroundColor: '#33A8FF', marginTop: '2%' }]}>
                <Text style={{ fontWeight: 'bold' }}>UPLOAD</Text>
              </TouchableOpacity>
            </View>
          </View>

        </View>{
          this.state.loading !== null ? (
            this.state.loading ? (
              <Spinner size="large" />
            ) : (
                <View>
                  <TextContainer
                    first="Uploaded! Address on IPFS:"
                    second={this.state.address}
                    link={() => Linking.openURL(this.state.address)}
                    style={{ color: 'blue', textDecorationLine: 'underline' }}
                  />

                  <TextContainer
                    first="Transaction Hash"
                    second={this.state.transactionHash}
                  />

                  <TextContainer
                    first="Block Hash"
                    second={this.state.blockHash}
                  />

                </View>
              )
          ) : null
        }
      </View>
    )
  }
  render() {
    return (
      <ScrollView style={styles.container}
        contentContainerStyle={{ flex: 1 }} >
        <View >
          <Header style={[{backgroundColor: '#33A8FF'}] } >
            <Body>{
              !this.state.clickUpload ? (
                <Title>VERITAS APP</Title>
              )
                : (
                  <Title> Upload to Blockchain </Title>
                )
            }

            </Body>
            <Right>
              <Button transparent onPress={() => this.setState({ clickUpload: !this.state.clickUpload })}>{
                !!this.state.clickUpload ?
                  (<Text> HOME </Text>)
                  : (<Text> ADD </Text>)
              }
              </Button>
            </Right>
          </Header>
        </View>
        {
          this.state.clickUpload ?
            (
              this.newUploadScreen()
            )
            :
            (
              <ScrollView style={{ flex: 1 }}
                contentContainerStyle={{ flex: 1 }}>
                {
                  this.state.fetchLoading ?
                    (
                      <View style={{ flex: 1, marginTop: '40%' }}>
                        <Spinner size='large' />
                      </View>
                    )
                    : (
                      <ScrollView style={{ flex: 1 }}
                        contentContainerStyle={{ flex: 1 }}
                      >
                      <Modal
                         animationType = {"slide"}
                         transparent={false}
                         visible={this.state.loginModalVisible}
                         onRequestClose={() => {
                         Alert.alert('Modal has now been closed.');
                       }}>

                              <View style = { [styles.container2,{ backgroundColor: "#33A8FF"}] }>
                                <Text style={{ fontSize:200}}>V</Text>
                                <Text style={{ fontSize:50}}>Veritas</Text>
                                       <View style={{ alignItems: 'center', marginTop: '1%', backgroundColor: 'white' }}>

                                         <TextInput
                                           placeholder="username"
                                           style={styles.label2}
                                           underlineColorAndroid="transparent"
                                         />
                                       </View>

                                       <View style={{ alignItems: 'center', marginTop: '1%', backgroundColor: 'white' }}>
                                         <TextInput
                                           placeholder="login"
                                           style={styles.label2}
                                           underlineColorAndroid="transparent"
                                           secureTextEntry={true}
                                         />
                                       </View>
                                       <TouchableOpacity onPress={() => {  this.displayLoginModal(!this.state.loginModalVisible);}  } style={[styles.uploadbutton, { justifyContent: 'center', backgroundColor: 'white', marginTop: '1%' }]}>
                                              <Text style={{ fontWeight: 'bold' }}>Login</Text>
                                       </TouchableOpacity>
                                </View>
                       </Modal>
                        <Fragment>
                          {
                            this.state.images.length === 0 ?
                              (
                                <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
                                  <TouchableOpacity onPress={() => this.setState({ clickUpload: !this.state.clickUpload })} style={[styles.label, { justifyContent: 'center', backgroundColor: '#8470ff' }]}>
                                    <Text style={{ fontWeight: 'bold' }}>  ADD </Text>
                                  </TouchableOpacity>
                                </View>
                              ) :
                              (
                               <View>

                                <FlatList
                                  data={this.state.images}
                                  extraData={this.state.images}
                                  keyExtractor={(item, index) => index.toString()}
                                  renderItem={(item, index) => {

                                    return (
                                      <TouchableOpacity onPress={() => { this.displayModal(true, item.item);}}>
                                      <View style = { styles.container2 }>
                                      <Modal
                                         animationType = {"slide"}
                                         transparent={false}
                                         visible={this.state.isVisible}
                                         onRequestClose={() => {
                                         Alert.alert('Modal has now been closed.');
                                       }}>
                                       <ScrollView style={{ flex: 1 }} contentContainerStyle={{ flex: 1 }}>
                                                       <View style = { [styles.container2, {marginTop: '3%' }]}>
                                                            <CachedImage
                                                              source={{ uri: this.state.modalData.imgipfsAddress }}
                                                              cacheKey={this.state.modalData.imgipfsHash}
                                                              style={{ width: 300, height: 300 }}
                                                            />
                                                           {/* <Image source={{ uri: this.state.modalData.imgipfsAddress }} style={{ width: 300, height: 300 }} /> */}
                                                            <Text style={{  marginTop: '2%' }}>
                                                             <B>Name:</B> {"\t"}{this.state.modalData.label} {"\n"}
                                                             <B>Article:</B>{"\n"}
                                                             {this.state.modalData.article} {"\n"}{"\n"}
                                                             <B>Location:</B>{"\t"} Hong Kong{"\n"}
                                                             <B>Date and Time:</B> {"\t"}{moment(this.state.modalData.createdAt).format("MMMM Do YYYY, h:mm:ss a")}{"\n"}
                                                             <B>IPFSAddress:</B> {"\t"}{this.state.modalData.imgipfsAddress} {"\n"}
                                                             <B>BlockHash:</B> {"\t"}{this.state.modalData.blockHash} {"\n"}
                                                             <B>Tags:</B> {"\t"}{this.state.modalData.tags} {"\n"}
                                                             <B>Article IPFS:</B> {"\t"}{this.state.modalData.articleipfsHash} {"\n"}

                                                            </Text>

                                                            <View style={{ alignItems: 'center', marginTop: '2%' }}>
                                                              <TouchableOpacity onPress={() => this.similarImages()} style={[styles.uploadbutton, { justifyContent: 'center', backgroundColor: '#33A8FF' }]}>
                                                                <Text style={{ fontWeight: 'bold' }}>Similar Images</Text>
                                                              </TouchableOpacity>
                                                            </View>

                                                            <TouchableOpacity onPress={() => {  this.displayModal(!this.state.isVisible, []);}  } style={[styles.uploadbutton, { justifyContent: 'center', backgroundColor: '#33A8FF', marginTop: '1%' }]}>
                                                              <Text style={{ fontWeight: 'bold' }}>Go Back</Text>
                                                            </TouchableOpacity>

                                                            <Fragment>
                                                              {
                                                                this.state.similarImages.length === 0 ?
                                                                  (
                                                                    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
                                                                    </View>
                                                                  ) :
                                                                  (
                                                                   <View>

                                                                    <FlatList
                                                                      data={this.state.similarImages}
                                                                      extraData={this.state.images}
                                                                      style = {{marginTop : '1%'}}
                                                                      keyExtractor={(item, index) => index.toString()}
                                                                      renderItem={(item, index) => {

                                                                        return (
                                                                          <View>
                                                                            <CachedImage
                                                                              source={{ uri: "https://gateway.ipfs.io/ipfs/"+item.item.ipfsHash }}
                                                                              cacheKey={item.item.ipfsHash}
                                                                              style={{ width: 300, height: 300 }}
                                                                            />
                                                                            {/* <Image source={{ uri: "https://gateway.ipfs.io/ipfs/"+item.item.ipfsHash }} style={{ width: 300, height: 300, alignItems: 'center' }} /> */}
                                                                            <Text ><B>IPFS Hash:</B> {item.item.ipfsHash}</Text>
                                                                            <Text ><B>Percentage</B>: {Math.round(item.item.percentage)} %</Text>
                                                                          </View>
                                                                        )

                                                                      }}
                                                                    />
                                                                    </View>

                                                                  )}
                                                            </Fragment>
                                                       </View>
                                              </ScrollView>
                                       </Modal>
                                       </View>
                                      <Card
                                        key={index}
                                        state={this.state}
                                        imghash = {item.item.imgipfsHash}
                                        createdAt={item.item.createdAt}
                                        address={item.item.imgipfsAddress}
                                        blockHash={item.item.blockHash}
                                        transactionHash={item.item.transactionHash}
                                        label={item.item.label}
                                        datetime={item.item.datetime}
                                      />
                                      </TouchableOpacity>
                                    )

                                  }}
                                />
                                </View>

                              )}
                        </Fragment>
                      </ScrollView>
                    )
                }
              </ScrollView>
            )
        }
      </ScrollView>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5FCFF',
  },
  container2: {
  padding: 25,
  flex: 1,
  alignItems: 'center',
  justifyContent: 'center',
},
  avatarContainer: {
    borderColor: '#9B9B9B',
    borderWidth: 1 / PixelRatio.get(),
    justifyContent: 'center',
    alignItems: 'center'
  },
  avatar: {
    width: width * 0.8,
    height: width * 1
  },
  label: {
    height: 40,
    width: width * 0.8,
    alignItems: 'center',
    paddingLeft: '8%',
    borderWidth: 1,
    borderBottomLeftRadius: 10,
    borderBottomRightRadius: 10,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  label2: {
    height: 40,
    width: width * 0.8,
    alignItems: 'center',
    paddingLeft: '8%',
    borderWidth: 1,

  },
  uploadbutton: {
    height: 40,
    width: width / 4,
    alignItems: 'center',
    borderWidth: 1,
    borderBottomLeftRadius: 10,
    borderBottomRightRadius: 10,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  closeText: {
  fontSize: 24,
  color: '#00479e',
  textAlign: 'center',
},
image: {
  marginTop: 150,
  marginBottom: 10,
  width: '100%',
  height: 350,
},
});

// <TextContainer
//   first="Label"
//   second={this.state.label}
// />
//
// <TextContainer
//   first="Hash"
//   second={this.state.hash}
// />
