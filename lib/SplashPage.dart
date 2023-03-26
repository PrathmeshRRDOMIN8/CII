import 'dart:async';

import 'package:ciihackathon/camera_page.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class MySplashPage extends StatefulWidget {
  const MySplashPage({Key? key}) : super(key: key);

  @override
  State<MySplashPage> createState() => _MySplashPageState();
}

class _MySplashPageState extends State<MySplashPage> {
  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    Timer(const Duration(seconds: 4), () {
      Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => CameraPage()));
    });
  }
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color(0xff42AA8F),
              Color(0xff466FA7),
            ],
            stops: [0.35,1],
          ),
        ),
        child: Scaffold(
          backgroundColor: Colors.transparent,
          body: SafeArea(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // logo here
                  SizedBox(
                    height: size.height*0.7,
                    width: size.width*0.7,
                    child: Lottie.network('https://assets9.lottiefiles.com/packages/lf20_VAdSJ6.json'),
                  ),
                  SizedBox(
                    height: size.height*0.05,
                  ),
                  Text(
                    "CII HACKATHON",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 24.0,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
  }
}
